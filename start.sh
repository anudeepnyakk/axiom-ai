#!/usr/bin/env bash
set -euo pipefail

# Start backend (Flask metrics server with API endpoints) in background
echo "[start.sh] Starting backend on port 8000..."
python scripts/start_metrics_server.py &

BACKEND_PID=$!

# Wait for backend to be alive (max 30s)
echo "[start.sh] Waiting for backend..."
for i in {1..30}; do
  if curl --silent --fail http://127.0.0.1:5000/health 2>/dev/null; then
    echo "[start.sh] Backend healthy."
    break
  fi
  echo "[start.sh] waiting... ($i)"
  sleep 1
done

# Set env var that frontend expects
export BACKEND_URL="http://127.0.0.1:5000"

# Run Streamlit frontend (use port 7860 which HF expects for Docker spaces)
echo "[start.sh] Starting Streamlit frontend..."
streamlit run streamlit_app.py --server.port 7860 --server.address 0.0.0.0

