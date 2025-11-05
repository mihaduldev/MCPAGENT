"""
Application settings using Pydantic BaseSettings
Loads configuration from environment variables and .env file
"""

from typing import Optional, List, Literal
from pathlib import Path
from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Application
    # ─────────────────────────────────────────────────────────────────
    app_name: str = Field(default="MCP Agent", description="Application name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", 
        description="Environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="1.0.0", description="Application version")
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: Literal["json", "text"] = Field(default="json")
    log_file: Optional[Path] = Field(default=Path("logs/mcpagent.log"))
    enable_file_logging: bool = Field(default=True)
    enable_console_logging: bool = Field(default=True)
    
    # ─────────────────────────────────────────────────────────────────
    # API Server
    # ─────────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_secret_key: SecretStr = Field(
        default=SecretStr("change-this-secret-key"),
        description="Secret key for API security"
    )
    api_prefix: str = Field(default="/api/v1")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Database
    # ─────────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./data/mcpagent.db",
        description="Database connection URL"
    )
    db_pool_size: int = Field(default=10, ge=1)
    db_max_overflow: int = Field(default=20, ge=0)
    db_pool_timeout: int = Field(default=30, ge=1)
    
    # ─────────────────────────────────────────────────────────────────
    # Redis Cache
    # ─────────────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    enable_cache: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=0)
    cache_max_size: int = Field(default=1000, ge=0)
    
    # ─────────────────────────────────────────────────────────────────
    # Vector Store
    # ─────────────────────────────────────────────────────────────────
    vector_store_type: Literal["chromadb", "faiss", "pinecone", "weaviate"] = Field(
        default="chromadb"
    )
    vector_store_path: Path = Field(default=Path("./data/vector_store"))
    
    # ChromaDB
    chroma_host: str = Field(default="localhost")
    chroma_port: int = Field(default=8001, ge=1, le=65535)
    chroma_collection_name: str = Field(default="mcpagent_docs")
    
    # Pinecone (optional)
    pinecone_api_key: Optional[SecretStr] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    
    # ─────────────────────────────────────────────────────────────────
    # LLM Configuration
    # ─────────────────────────────────────────────────────────────────
    llm_provider: Literal["openai", "anthropic", "gemini", "ollama", "groq"] = Field(
        default="openai"
    )
    
    # OpenAI
    openai_api_key: Optional[SecretStr] = None
    openai_model: str = Field(default="gpt-4-turbo-preview")
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    openai_max_tokens: int = Field(default=4096, ge=1)
    
    # Anthropic
    anthropic_api_key: Optional[SecretStr] = None
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    
    # Google Gemini
    google_api_key: Optional[SecretStr] = None
    gemini_model: str = Field(default="gemini-1.5-pro")
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.2")
    
    # Groq
    groq_api_key: Optional[SecretStr] = None
    groq_model: str = Field(default="mixtral-8x7b-32768")
    
    # ─────────────────────────────────────────────────────────────────
    # Embeddings
    # ─────────────────────────────────────────────────────────────────
    embedding_provider: Literal["openai", "huggingface", "sentence-transformers"] = Field(
        default="openai"
    )
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimension: int = Field(default=1536, ge=1)
    
    # ─────────────────────────────────────────────────────────────────
    # RAG Configuration
    # ─────────────────────────────────────────────────────────────────
    chunk_size: int = Field(default=1000, ge=100)
    chunk_overlap: int = Field(default=200, ge=0)
    max_chunk_size: int = Field(default=2000, ge=100)
    
    retrieval_k: int = Field(default=5, ge=1, description="Number of docs to retrieve")
    retrieval_score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_reranking: bool = Field(default=True)
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-12-v2")
    
    enable_hybrid_search: bool = Field(default=True)
    semantic_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # ─────────────────────────────────────────────────────────────────
    # Agent Configuration
    # ─────────────────────────────────────────────────────────────────
    agent_max_iterations: int = Field(default=10, ge=1)
    agent_timeout: int = Field(default=300, ge=1)
    enable_multi_agent: bool = Field(default=True)
    agent_memory_type: Literal["ephemeral", "persistent"] = Field(default="persistent")
    
    # ─────────────────────────────────────────────────────────────────
    # MCP (Model Context Protocol)
    # ─────────────────────────────────────────────────────────────────
    mcp_server_timeout: int = Field(default=30, ge=1)
    mcp_retry_attempts: int = Field(default=3, ge=0)
    mcp_retry_delay: int = Field(default=1, ge=0)
    mcp_max_concurrent_connections: int = Field(default=5, ge=1)
    
    # ─────────────────────────────────────────────────────────────────
    # Authentication & Security
    # ─────────────────────────────────────────────────────────────────
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("change-this-jwt-secret"),
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    
    enable_api_key_auth: bool = Field(default=True)
    api_keys: List[str] = Field(default=["test-key-123"])
    
    enable_rate_limiting: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60, ge=1)
    rate_limit_burst: int = Field(default=10, ge=1)
    
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: List[str] = Field(default=["*"])
    
    # ─────────────────────────────────────────────────────────────────
    # Monitoring & Observability
    # ─────────────────────────────────────────────────────────────────
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    metrics_path: str = Field(default="/metrics")
    
    enable_tracing: bool = Field(default=False)
    otel_exporter_otlp_endpoint: Optional[str] = None
    trace_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    
    enable_sentry: bool = Field(default=False)
    sentry_dsn: Optional[str] = None
    
    # ─────────────────────────────────────────────────────────────────
    # Feature Flags
    # ─────────────────────────────────────────────────────────────────
    enable_document_ingestion: bool = Field(default=True)
    enable_web_scraping: bool = Field(default=True)
    enable_code_execution: bool = Field(default=False)
    enable_image_processing: bool = Field(default=False)
    enable_voice_input: bool = Field(default=False)
    
    # ─────────────────────────────────────────────────────────────────
    # Document Processing
    # ─────────────────────────────────────────────────────────────────
    supported_file_types: List[str] = Field(
        default=["pdf", "docx", "txt", "md", "html", "json", "csv"]
    )
    max_file_size_mb: int = Field(default=50, ge=1)
    document_storage_path: Path = Field(default=Path("./data/documents"))
    
    # ─────────────────────────────────────────────────────────────────
    # Performance & Optimization
    # ─────────────────────────────────────────────────────────────────
    request_timeout: int = Field(default=120, ge=1)
    enable_streaming: bool = Field(default=True)
    stream_chunk_size: int = Field(default=512, ge=1)
    
    enable_background_tasks: bool = Field(default=True)
    task_queue_type: Literal["memory", "redis", "celery"] = Field(default="redis")
    
    # ─────────────────────────────────────────────────────────────────
    # Development & Testing
    # ─────────────────────────────────────────────────────────────────
    testing: bool = Field(default=False)
    mock_llm: bool = Field(default=False)
    mock_vector_store: bool = Field(default=False)
    seed_database: bool = Field(default=False)
    
    # ─────────────────────────────────────────────────────────────────
    # External Services
    # ─────────────────────────────────────────────────────────────────
    firecrawl_api_key: Optional[SecretStr] = None
    serper_api_key: Optional[SecretStr] = None
    tavily_api_key: Optional[SecretStr] = None
    wolfram_alpha_app_id: Optional[SecretStr] = None
    
    # ─────────────────────────────────────────────────────────────────
    # Validators
    # ─────────────────────────────────────────────────────────────────
    @field_validator("semantic_weight", "keyword_weight")
    @classmethod
    def validate_weights(cls, v: float, info) -> float:
        """Validate that weights sum to 1.0"""
        return v
    
    @field_validator("log_file", "vector_store_path", "document_storage_path")
    @classmethod
    def create_directories(cls, v: Optional[Path]) -> Optional[Path]:
        """Create directories if they don't exist"""
        if v:
            v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    # ─────────────────────────────────────────────────────────────────
    # Computed Properties
    # ─────────────────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.app_env == "development"
    
    @property
    def database_is_sqlite(self) -> bool:
        """Check if using SQLite"""
        return self.database_url.startswith("sqlite")
    
    @property
    def database_is_postgres(self) -> bool:
        """Check if using PostgreSQL"""
        return self.database_url.startswith("postgresql")
    
    def get_llm_api_key(self) -> Optional[str]:
        """Get API key for current LLM provider"""
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "gemini": self.google_api_key,
            "groq": self.groq_api_key,
        }
        key = key_map.get(self.llm_provider)
        return key.get_secret_value() if key else None


# Global settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create required directories"""
    directories = [
        "data",
        "data/documents",
        "data/vector_store",
        "logs",
        "tmp",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


ensure_directories()

