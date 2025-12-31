@echo off
cd /d %~dp0

echo ==========================================
echo      Bank System - Run from Source
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! To run from source, you must install Python 3.10+.
    pause
    exit /b
)

echo [1/2] Checking dependencies (Offline Mode Supported)...
if exist "packages" (
    echo Found local packages. Installing offline...
    pip install --no-index --find-links=packages -r requirements.txt
) else (
    echo Installing from PyPI...
    pip install -r requirements.txt
)
echo.

echo [2/2] Starting Server...
echo Access at: http://localhost:8000
echo (Press Ctrl+C to stop)
python main.py

pause
