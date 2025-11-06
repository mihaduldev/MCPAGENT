@echo off
echo ========================================
echo   Starting Docker Services
echo   PostgreSQL + Redis
echo ========================================
echo.

echo [*] Starting PostgreSQL and Redis...
docker-compose -f docker-compose.services.yml up -d

echo.
echo [*] Waiting for services to be ready...
timeout /t 5 /nobreak > nul

echo.
echo [*] Checking service status...
docker-compose -f docker-compose.services.yml ps

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo PostgreSQL: localhost:5432
echo   Database: mcpagent
echo   Username: mcpagent
echo   Password: mcpagent_password
echo.
echo Redis: localhost:6379
echo.
echo Connection Strings:
echo   DATABASE_URL=postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent
echo   REDIS_URL=redis://localhost:6379/0
echo.
echo ========================================
echo.
echo Next steps:
echo   1. Update your .env file with the connection strings above
echo   2. Run: venv\Scripts\activate
echo   3. Run: python -m uvicorn src.api.main:app --reload
echo.

pause

