@echo off
cd /d %~dp0

echo ==========================================
echo      Bank System - One-Click Build
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+ and add to PATH.
    pause
    exit /b
)

echo [1/2] Installing build tools (if missing)...
pip install -r requirements.txt
echo.

echo [2/2] Building EXE...
python build_exe.py

echo.
echo ==========================================
if exist dist\BankContractSystem.exe (
    echo [SUCCESS] BankContractSystem.exe created in 'dist' folder!
) else (
    echo [FAILED] Build failed. Please checks errors above.
)
echo ==========================================
pause
