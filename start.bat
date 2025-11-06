@echo off
echo ========================================
echo   MCPAGENT - Starting Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if dependencies are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    echo [OK] Dependencies installed
    echo.
)

REM Start the server
echo [*] Starting MCPAGENT server on http://localhost:8000
echo [*] API docs: http://localhost:8000/docs
echo [*] Press Ctrl+C to stop
echo.
echo ========================================
echo.

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

pause

