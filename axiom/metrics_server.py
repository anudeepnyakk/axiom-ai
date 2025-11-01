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
    
Then visit: http://localhost:8000/metrics
"""

import logging
from flask import Flask, Response
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


@app.route('/')
def index():
    """
    Root endpoint with basic information.
    
    Returns:
        str: Welcome message with available endpoints
    """
    return """
    <html>
    <head><title>Axiom AI Metrics Server</title></head>
    <body>
        <h1>Axiom AI Metrics Server</h1>
        <p>Prometheus-compatible metrics for the Axiom AI RAG system.</p>
        
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/metrics">/metrics</a> - Prometheus metrics (text format)</li>
            <li><a href="/health">/health</a> - Health check (JSON)</li>
        </ul>
        
        <h2>Exposed Metrics:</h2>
        <ul>
            <li><strong>axiom_request_count</strong> - Total requests per stage</li>
            <li><strong>axiom_error_count</strong> - Total errors per stage</li>
            <li><strong>axiom_latency_seconds</strong> - Latency histogram per stage</li>
        </ul>
        
        <h2>Example Usage:</h2>
        <pre>
# View metrics in browser
http://localhost:8000/metrics

# Query with curl
curl http://localhost:8000/metrics

# Configure Prometheus scraper
scrape_configs:
  - job_name: 'axiom-ai'
    static_configs:
      - targets: ['localhost:8000']
        </pre>
    </body>
    </html>
    """


def run_server(host='0.0.0.0', port=8000, debug=False):
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

