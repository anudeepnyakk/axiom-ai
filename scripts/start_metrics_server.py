"""
Start Axiom AI Metrics Server

Simple script to launch the Prometheus metrics HTTP endpoint.

Usage:
    python scripts/start_metrics_server.py
    
Then visit:
    http://localhost:8000/metrics    - Prometheus metrics
    http://localhost:8000/health     - Health check
    http://localhost:8000/           - Info page
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.metrics_server import run_server


if __name__ == '__main__':
    print("=" * 60)
    print("AXIOM AI - METRICS SERVER")
    print("=" * 60)
    print()
    print("Starting Prometheus metrics endpoint...")
    print()
    print("📊 Metrics:  http://localhost:8000/metrics")
    print("💚 Health:   http://localhost:8000/health")
    print("ℹ️  Info:     http://localhost:8000/")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        run_server(host='0.0.0.0', port=8000, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down metrics server...")
        print("Goodbye! 👋")

