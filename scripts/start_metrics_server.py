"""
Start Axiom AI Metrics Server

Simple script to launch the Prometheus metrics HTTP endpoint.

Usage:
    python scripts/start_metrics_server.py
    
Environment Variables:
    METRICS_PORT: Port to run on (default: 5000)
    
Then visit:
    http://localhost:5000/metrics    - Prometheus metrics
    http://localhost:5000/health     - Health check
    http://localhost:5000/           - Info page
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.metrics_server import run_server


if __name__ == '__main__':
    port = int(os.getenv('METRICS_PORT', '5000'))
    
    print("=" * 60)
    print("AXIOM AI - METRICS SERVER")
    print("=" * 60)
    print()
    print("Starting Prometheus metrics endpoint...")
    print()
    print(f"📊 Metrics:  http://localhost:{port}/metrics")
    print(f"💚 Health:   http://localhost:{port}/health")
    print(f"ℹ️  Info:     http://localhost:{port}/")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        run_server(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down metrics server...")
        print("Goodbye! 👋")

