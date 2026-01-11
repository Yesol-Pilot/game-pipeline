@echo off
echo [Game Factory Control Center] Initializing...
echo.

REM Check if FastAPI is installed
python -c "import fastapi" 2>NUL
if %errorlevel% neq 0 (
    echo [ERROR] FastAPI not found. Please run: pip install -r requirements.txt
    pause
    exit /b
)

echo Starting Server at http://localhost:8000
echo Press Ctrl+C to stop.
echo.
python -m uvicorn web_dashboard.main:app --reload --host 0.0.0.0 --port 8000

pause
