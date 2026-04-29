#!/bin/bash
# Double-click this file to launch ReminderHub.
# It starts both the backend and frontend, then opens the app in your browser.

set -e
cd "$(dirname "$0")"

PROJECT_DIR="$(pwd)"
VENV_PYTHON="/Users/josephardizzone/Desktop/Claude/.venv/bin/uvicorn"
LOG_DIR="$PROJECT_DIR/.logs"
mkdir -p "$LOG_DIR"

# kill any existing reminderhub servers
pkill -f "uvicorn main:app --port 8000" 2>/dev/null || true
pkill -f "vite.*reminderhub" 2>/dev/null || true
sleep 1

echo "Starting ReminderHub..."

# backend
cd "$PROJECT_DIR/backend"
nohup "$VENV_PYTHON" main:app --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  backend (pid $BACKEND_PID) → http://localhost:8000"

# frontend
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "  frontend (pid $FRONTEND_PID) → http://localhost:5173"

# wait for frontend to be ready
echo "  waiting for dev server..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

open "http://localhost:5173"

echo ""
echo "ReminderHub is running. Logs: $LOG_DIR/"
echo "To stop, run: pkill -f 'uvicorn main:app' && pkill -f 'vite.*reminderhub'"
echo ""

# keep terminal open for 3s so the user can read the output
sleep 3
