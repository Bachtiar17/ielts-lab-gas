#!/usr/bin/env bash
set -euo pipefail

# IELTS Lab — One-Click Launcher for macOS & Linux
# Automatically sets up Python & Node dependencies on first run and opens http://localhost:3000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="$HOME/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "============================================"
echo "  IELTS Lab — Starting Local Workbench"
echo "============================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3.11+ is required. Download it from https://www.python.org/downloads/"
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js 20+ is required. Download the installer from https://nodejs.org/"
  exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "[Setup] Created .env from .env.example (optional: add GEMINI_API_KEY later in UI or .env)."
fi

if [ ! -d ".venv" ]; then
  echo "[Setup] Creating Python virtual environment (.venv)..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip >/dev/null
  echo "[Setup] Installing backend packages (first run only)..."
  .venv/bin/pip install -e .
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "[Setup] Installing frontend packages (first run only)..."
  (cd frontend && npm install --no-audit --no-fund)
fi

if [ ! -f "frontend/.env.local" ]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

cleanup() {
  echo ""
  echo "Stopping IELTS Lab servers..."
  kill "${BACKEND_PID:-}" "${FRONTEND_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ..."
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 >/tmp/ielts_lab_backend.log 2>&1 &
BACKEND_PID=$!

echo "[2/2] Starting Next.js web app on http://localhost:3000 ..."
(cd frontend && npm run dev -- -H 127.0.0.1 -p 3000) >/tmp/ielts_lab_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait until frontend responds, then open browser automatically
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:3000 >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ""
echo "IELTS Lab is ready at: http://localhost:3000"
echo "Press Ctrl+C in this window to stop both servers."

if command -v open >/dev/null 2>&1; then
  open "http://localhost:3000"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:3000"
fi

wait
