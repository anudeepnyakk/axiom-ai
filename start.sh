#!/usr/bin/env bash
echo "[DBG] start.sh invoked. pwd: $(pwd) user: $(whoami) ls:" 
ls -la
echo "[DBG] Environment variables:"
env | sort
echo "[DBG] --------------------------"
set -euo pipefail

echo "[start.sh] Starting backend on port 5000..."
python scripts/start_metrics_server.py &

BACKEND_PID=$!

echo "[start.sh] Waiting for backend..."
for i in {1..30}; do
  if curl --silent --fail http://127.0.0.1:5000/health 2>/dev/null; then
    echo "[start.sh] Backend healthy."
    break
  fi
  echo "[start.sh] waiting... ($i)"
  sleep 1
done

export BACKEND_URL="http://127.0.0.1:5000"

echo "[start.sh] Starting Streamlit frontend..."
streamlit run streamlit_app.py --server.port 7860 --server.address 0.0.0.0
