@echo off
echo ===================================================
echo   Starting Vettora Backend & Frontend Servers...
echo ===================================================

start "Vettora Backend API" cmd /k "cd /d %~dp0backend && .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
start "Vettora Frontend UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Servers launched!
echo - Backend API: http://localhost:8000 (Docs at http://localhost:8000/docs)
echo - Frontend UI:  http://localhost:5173
echo ===================================================
