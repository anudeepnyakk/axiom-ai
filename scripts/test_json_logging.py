"""
Test Script for JSON Logging with Request ID Correlation

This script demonstrates the structured JSON logging with request ID tracking.
Run it to see how a single query generates correlated logs across all pipeline stages.

Usage:
    python scripts/test_json_logging.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.config.loader import load_config
from axiom.core.factory import create_query_engine
from axiom.logging_setup import setup_logging

def main():
    """Test JSON logging with a sample query."""
    
    print("=" * 70)
    print("AXIOM AI - JSON LOGGING TEST")
    print("=" * 70)
    print()
    print("This test will:")
    print("1. Enable JSON logging")
    print("2. Run a sample query")
    print("3. Show correlated logs with request_id")
    print()
    print("=" * 70)
    print()
    
    # Load config
    config = load_config()
    
    # Enable JSON logging
    print("[OK] Enabling JSON logging...")
    setup_logging(config.logging, use_json=True)
    print()
    
    # Create query engine
    print("[OK] Creating query engine...")
    query_engine = create_query_engine(config)
    print()
    
    # Run test query
    test_question = "What is Axiom AI?"
    print(f"[OK] Running test query: \"{test_question}\"")
    print()
    print("-" * 70)
    print("JSON LOGS (each line is a complete JSON object):")
    print("-" * 70)
    print()
    
    try:
        result = query_engine.query(test_question, top_k=3)
        
        print()
        print("-" * 70)
        print()
        print("[OK] Query completed successfully!")
        print()
        print(f"Answer: {result.answer[:200]}...")
        print(f"Retrieved {len(result.context_chunks)} context chunks")
        print()
        
    except Exception as e:
        print()
        print(f"[ERROR] Query failed: {e}")
        print()
    
    print("=" * 70)
    print()
    print("[TIP] HOW TO USE THE REQUEST ID:")
    print()
    print("1. Look for 'request_id' field in the JSON logs above")
    print("2. Copy the request_id value (e.g., 'a7f3c2d1')")
    print("3. Use it to filter logs:")
    print()
    print("   # Linux/Mac:")
    print("   grep 'a7f3c2d1' axiom.log | jq '.'")
    print()
    print("   # Windows PowerShell:")
    print("   Select-String 'a7f3c2d1' axiom.log")
    print()
    print("4. You'll see ALL logs for that specific request!")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()

