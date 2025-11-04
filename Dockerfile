# Dockerfile for Backend API Server (Railway/Render/Fly.io)
# Optimized for backend deployment - CPU-only, smaller dependencies
# Updated: 2025-11-02 - Fixed Railway timeout with CPU-only torch

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip first (for better caching)
RUN pip install --no-cache-dir --upgrade pip

# Install CPU-only PyTorch first (smaller, faster than CUDA version)
# This prevents sentence-transformers from pulling the huge CUDA torch
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

# Install lightweight dependencies first
RUN pip install --no-cache-dir \
    flask>=2.3.0 \
    prometheus-client>=0.18.0 \
    requests>=2.31.0 \
    openai<2.0.0 \
    pypdf>=3.0.0 \
    tiktoken>=0.5.0 \
    PyYAML>=6.0 \
    numpy<2.0 \
    scikit-learn>=1.3.0 \
    chardet>=5.0.0

# Install heavy ML dependencies last (after torch is already installed)
RUN pip install --no-cache-dir \
    sentence-transformers==2.7.0 \
    chromadb<0.5

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

