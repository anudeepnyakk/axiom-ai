"""
Axiom AI Metrics Server

This module provides an HTTP endpoint that exposes Prometheus-format metrics
for monitoring system health, performance, and usage.

The /metrics endpoint returns:
- Request counts per pipeline stage
- Error counts per pipeline stage  
- Latency histograms per pipeline stage

Usage:
    python -m axiom.metrics_server
    
Then visit: http://localhost:5000/metrics
"""

import logging
import os
from pathlib import Path
from flask import Flask, Response, request, jsonify
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from axiom.metrics import REQUEST_COUNT, ERROR_COUNT, LATENCY_SECONDS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route('/metrics')
def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns all registered metrics in Prometheus text format.
    This can be scraped by Prometheus, Grafana, Datadog, etc.
    
    Returns:
        Response: Prometheus-formatted metrics with appropriate content type
    """
    logger.debug("Metrics endpoint accessed")
    
    # generate_latest() collects all registered Prometheus metrics
    # and formats them in the standard Prometheus exposition format
    metrics_output = generate_latest()
    
    return Response(metrics_output, mimetype=CONTENT_TYPE_LATEST)


@app.route('/health')
def health():
    """
    Health check endpoint.
    
    Returns a simple JSON response indicating the service is running.
    Useful for load balancers and orchestration systems.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": "axiom-metrics",
        "version": "1.0.0"
    }


@app.route('/api/query', methods=['POST'])
def query():
    """RAG query endpoint"""
    try:
        from axiom.config.loader import load_config
        from axiom.core.factory import create_query_engine
        
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400
        
        question = data['question']
        top_k = data.get('top_k', 3)
        
        if not hasattr(app, 'query_engine'):
            config = load_config()
            app.query_engine = create_query_engine(config)
        
        result = app.query_engine.query(question, top_k=top_k)
        
        return jsonify({
            "answer": result.answer,
            "sources": [
                {
                    "text": chunk.text[:500] + "..." if len(chunk.text) > 500 else chunk.text,
                    "metadata": chunk.metadata
                }
                for chunk in result.context_chunks
            ]
        })
        
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        return jsonify({"error": str(e), "answer": None, "sources": []}), 500


@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload and process document endpoint"""
    try:
        from axiom.config.loader import load_config
        from axiom.core.factory import create_document_processor
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file temporarily
        upload_dir = Path('axiom/data')
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        # Process document
        config = load_config()
        processor = create_document_processor(config)
        chunks = processor.process_document(str(file_path))
        
        # Clean up temp file
        if file_path.exists():
            file_path.unlink()
        
        return jsonify({
            "success": True,
            "filename": file.filename,
            "chunks": len(chunks) if chunks else 0
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/')
def index():
    """
    Root endpoint with basic information.
    
    Returns:
        str: Welcome message with available endpoints
    """
    return """
    <html>
    <head><title>Axiom AI Backend API</title></head>
    <body>
        <h1>Axiom AI Backend API</h1>
        <p>RAG backend API for the Axiom AI system.</p>
        
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/metrics">/metrics</a> - Prometheus metrics (text format)</li>
            <li><a href="/health">/health</a> - Health check (JSON)</li>
            <li><strong>POST /api/query</strong> - Query RAG system (JSON body: {"question": "..."})</li>
            <li><strong>POST /api/upload</strong> - Upload document (multipart/form-data with "file" field)</li>
        </ul>
        
        <h2>Example Usage:</h2>
        <pre>
# Query RAG system
curl -X POST http://localhost:5000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What is this about?", "top_k": 3}'

# Upload document
curl -X POST http://localhost:5000/api/upload \\
  -F "file=@document.pdf"
        </pre>
    </body>
    </html>
    """


def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Start the metrics server.
    
    Args:
        host (str): Host to bind to (default: 0.0.0.0 for all interfaces)
        port (int): Port to bind to (default: 8000)
        debug (bool): Enable Flask debug mode (default: False)
    """
    logger.info(f"Starting Axiom AI Metrics Server on {host}:{port}")
    logger.info(f"Metrics endpoint: http://{host}:{port}/metrics")
    logger.info(f"Health check: http://{host}:{port}/health")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Run the server when executed directly
    run_server()

