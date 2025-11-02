# Dockerfile for HuggingFace Spaces (Docker SDK + Streamlit Template)
# Optimized for HuggingFace Spaces deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements-streamlit.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-streamlit.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p chroma_db axiom/data_samples logs

# Expose Streamlit port (HuggingFace Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check (HuggingFace Spaces compatible)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Run Streamlit app (HuggingFace Spaces convention: streamlit_app.py)
CMD streamlit run streamlit_app.py --server.port=7860 --server.address=0.0.0.0 --server.headless=true
