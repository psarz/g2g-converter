@echo off
REM Quick Setup Script for GitLab to GitHub CI/CD Converter (Windows)

echo.
echo ================================
echo GitLab to GitHub CI/CD Converter
echo Setup Script for Windows
echo ================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is required but not installed.
    pause
    exit /b 1
)
python --version
echo.

REM Setup Backend
echo Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo Backend setup complete!
echo.

REM Create .env file if not exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env created (configure as needed)
)

cd ..

REM Display next steps
echo.
echo Setup Complete!
echo.
echo Next steps:
echo 1. Start backend API:
echo    cd backend
echo    venv\Scripts\activate
echo    python run.py
echo.
echo 2. In another terminal, start frontend:
echo    cd frontend
echo    python -m http.server 8000
echo.
echo 3. Open http://localhost:8000 in your browser
echo.
echo For Docker setup:
echo    docker-compose up
echo.
pause
