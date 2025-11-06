@echo off
echo ========================================
echo   Stopping Docker Services
echo ========================================
echo.

docker-compose -f docker-compose.services.yml down

echo.
echo ========================================
echo   Services Stopped!
echo ========================================
echo.

pause

