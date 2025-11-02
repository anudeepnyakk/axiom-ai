# Dockerfile for Backend API Server (Railway/Render/Fly.io)
# Optimized for backend deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only backend requirements (not streamlit)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask prometheus-client requests

# Install backend dependencies
RUN pip install --no-cache-dir \
    sentence-transformers \
    chromadb \
    tiktoken \
    pypdf \
    PyYAML \
    numpy \
    scikit-learn \
    chardet \
    openai

# Copy only backend code (exclude frontend)
COPY axiom/ ./axiom/
COPY scripts/start_metrics_server.py ./scripts/
COPY config.yaml .

# Create necessary directories
RUN mkdir -p chroma_db logs

# Expose port (Railway uses PORT env var)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Run Flask server (Railway provides PORT env var)
CMD python scripts/start_metrics_server.py

