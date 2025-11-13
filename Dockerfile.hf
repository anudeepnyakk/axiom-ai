# Dockerfile for HuggingFace Spaces Docker mode
# Runs both backend (Flask) and frontend (Streamlit) in same container

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgomp1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all files
COPY . /app

# Install pip first
RUN pip install --no-cache-dir --upgrade pip

# Install CPU-only PyTorch first (smaller, faster)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

# Install all dependencies
RUN pip install --no-cache-dir \
    "flask>=2.3.0" \
    "flask-cors>=4.0.0" \
    "streamlit>=1.28.0" \
    "prometheus-client>=0.18.0" \
    "requests>=2.31.0" \
    "openai<2.0.0" \
    "pypdf>=3.0.0" \
    "tiktoken>=0.5.0" \
    "PyYAML>=6.0" \
    "numpy<2.0" \
    "scikit-learn>=1.3.0" \
    "chardet>=5.0.0" \
    "sentence-transformers==2.7.0" \
    "chromadb<0.5"

# Create necessary directories
RUN mkdir -p chroma_db logs axiom/data

# Make start script executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 5000 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BACKEND_URL=http://127.0.0.1:5000

# Run start script
CMD ["/app/start.sh"]

