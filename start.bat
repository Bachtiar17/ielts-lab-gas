@echo off
setlocal
REM IELTS Lab — One-Click Launcher for Windows

cd /d "%~dp0"

echo ============================================
echo   IELTS Lab — Starting Local Workbench
echo ============================================

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python 3.11+ is required. Download from https://www.python.org/downloads/
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js 20+ is required. Download from https://nodejs.org/
  pause
  exit /b 1
)

if not exist ".env" (
  if exist ".env.example" copy ".env.example" ".env" >nul
)

if not exist ".venv" (
  echo [Setup] Creating Python virtual environment...
  python -m venv .venv
  .venv\Scripts\pip install --upgrade pip >nul
  echo [Setup] Installing backend packages (first run only)...
  .venv\Scripts\pip install -e .
)

if not exist "frontend\node_modules" (
  echo [Setup] Installing frontend packages (first run only)...
  pushd frontend
  call npm install --no-audit --no-fund
  popd
)

if not exist "frontend\.env.local" (
  echo NEXT_PUBLIC_API_URL=http://localhost:8000> frontend\.env.local
)

echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
start "IELTS Lab Backend" cmd /c ".venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Starting Next.js web app on http://localhost:3000 ...
start "IELTS Lab Frontend" cmd /c "cd frontend && npm run dev -- -H 127.0.0.1 -p 3000"

timeout /t 5 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo IELTS Lab is opening at http://localhost:3000
echo Close the two server windows whenever you finish practicing.
pause
