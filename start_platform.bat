@echo off
title Behavioral Biometric Banking Platform Launcher
echo =========================================================
echo   Starting AI-Powered Behavioral Biometric Platform...
echo =========================================================

echo [1/3] Starting FastAPI Core Banking and Security Backend (Port 8001)...
start "BBS Backend [Port 8001]" cmd /k "cd /d "%~dp0" && set PYTHONPATH=%~dp0backend;%~dp0 && "%~dp0backend\venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --app-dir backend"

echo [2/3] Starting Customer Banking Portal (Port 3002)...
start "BBS Customer Portal [Port 3002]" cmd /k "cd /d "%~dp0frontend" && npm run dev -- -p 3002"

echo [3/3] Starting Security and MLOps Operations Dashboard (Port 3001)...
start "BBS SecOps Console [Port 3001]" cmd /k "cd /d "%~dp0security-dashboard" && npm run dev"

echo =========================================================
echo   All microservices launched in separate windows!
echo   - Backend and API Docs: http://localhost:8001/docs
echo   - Customer Portal:      http://localhost:3002
echo   - SecOps Dashboard:     http://localhost:3001/console/alerts
echo =========================================================
echo Launcher script completed successfully.
exit /b 0
