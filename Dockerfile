# Dockerfile for Backend API Server (Railway/Render/Fly.io)
# Optimized for backend deployment - backend-only dependencies
# Updated: 2025-11-02 - Force rebuild to fix Railway timeout

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first (for better layer caching)
COPY requirements-backend.txt .

# Install backend dependencies only (excludes frontend deps like nicegui/streamlit)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-backend.txt

# Copy only backend code (exclude frontend via .dockerignore)
COPY axiom/ ./axiom/
COPY scripts/start_metrics_server.py ./scripts/
COPY config.yaml .

# Create necessary directories
RUN mkdir -p chroma_db logs

# Expose port (Railway uses PORT env var)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check (using curl instead of python requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run Flask server (Railway provides PORT env var)
CMD python scripts/start_metrics_server.py

