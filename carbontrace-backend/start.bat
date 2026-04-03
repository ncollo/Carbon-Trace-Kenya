@echo off
title CarbonTrace Kenya - Backend API

echo ================================================
echo   CarbonTrace Kenya - Backend API
echo   EPRA Hackathon 2026 - Team EmitIQ
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Install Python 3.12 from https://python.org and tick "Add Python to PATH"
    pause
    exit /b 1
)
echo Python found:
python --version
echo.

echo [1/4] Installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install fastapi "uvicorn[standard]" sqlalchemy pandas scikit-learn numpy python-multipart aiofiles pdfplumber --quiet

if errorlevel 1 (
    echo ERROR: pip install failed. Try running as Administrator.
    pause
    exit /b 1
)
echo     Dependencies installed OK

echo.
echo [2/4] Seeding database from bundled CSV datasets...
python seed.py
if errorlevel 1 (
    echo ERROR: Database seeding failed.
    pause
    exit /b 1
)

echo.
echo [3/4] Training Isolation Forest model...
python ml_models.py
if errorlevel 1 (
    echo ERROR: Model training failed.
    pause
    exit /b 1
)

echo.
echo [4/4] Starting FastAPI server...
echo.
echo   API running at : http://localhost:8000
echo   API docs       : http://localhost:8000/docs
echo   Health check   : http://localhost:8000/api/health
echo.
echo   Keep this window open.
echo   Open a second PowerShell window for the frontend.
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
