"""
FastAPI main application with production features
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.config.logging import get_logger
from src.infrastructure.database import init_db
from src.utils.metrics import metrics_registry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.app_env}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize vector store
    from src.core.rag import rag_system
    if rag_system.available:
        logger.info("✓ RAG system ready")
    else:
        logger.warning("⚠ RAG system unavailable")
    
    # Initialize cache
    from src.infrastructure.cache.redis_cache import cache
    if cache.enabled:
        logger.info("✓ Cache ready")
    else:
        logger.warning("⚠ Cache unavailable")
    
    logger.info(f"{settings.app_name} started successfully")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Production-grade AI Agent System with RAG and multi-agent orchestration",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# ─────────────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────────────

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Update metrics
    metrics_registry.request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    metrics_registry.request_latency.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Exception Handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc} - {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "message": "An unexpected error occurred",
                "detail": str(exc) if settings.debug else "Internal server error"
            }
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Root Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "environment": settings.app_env,
        "status": "running",
        "docs": "/docs",
        "api": settings.api_prefix
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from src.infrastructure.database import engine
    from src.infrastructure.cache.redis_cache import cache
    from src.core.rag import rag_system
    
    # Check database
    db_healthy = True
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    # Check services
    services = {
        "database": "healthy" if db_healthy else "unhealthy",
        "cache": "healthy" if cache.enabled else "disabled",
        "vector_store": "healthy" if rag_system.available else "unhealthy",
        "llm": "configured" if settings.get_llm_api_key() else "not_configured"
    }
    
    # Overall status
    is_healthy = all(
        status in ["healthy", "disabled", "configured"] 
        for status in services.values()
    )
    
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "version": settings.version,
            "environment": settings.app_env,
            "services": services,
            "timestamp": time.time()
        }
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.enable_metrics:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Metrics disabled"}
        )
    
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    metrics_data = generate_latest(metrics_registry.registry)
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# ─────────────────────────────────────────────────────────────────────────────
# API Routes (would be imported from separate modules)
# ─────────────────────────────────────────────────────────────────────────────

# TODO: Import and include API routers here
# from src.api.v1 import chat, documents, agents, users
# app.include_router(chat.router, prefix=f"{settings.api_prefix}/chat", tags=["chat"])
# app.include_router(documents.router, prefix=f"{settings.api_prefix}/documents", tags=["documents"])
# app.include_router(agents.router, prefix=f"{settings.api_prefix}/agents", tags=["agents"])
# app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["users"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

