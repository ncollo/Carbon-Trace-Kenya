@echo off
title CarbonTrace Kenya - Frontend

echo ================================================
echo   CarbonTrace Kenya - Frontend
echo   EPRA Hackathon 2026 - Team EmitIQ
echo ================================================
echo.
echo Make sure the backend is running first!
echo Start: carbontrace-backend\start.bat
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found.
    echo Install Node.js 18 LTS from https://nodejs.org
    pause
    exit /b 1
)

echo Node.js found:
node --version
echo.

echo Installing frontend dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed.
    pause
    exit /b 1
)

echo.
echo Starting frontend...
echo Open browser at: http://localhost:5173
echo.
call npm run dev
pause
