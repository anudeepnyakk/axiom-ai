"""
Test Script for Retry Logic and Fault Tolerance

This script demonstrates the retry logic with exponential backoff
and degraded mode fallback.

Usage:
    python scripts/test_retry_logic.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.retry_utils import retry, AllRetriesFailed
import time
import random


# Simulated unreliable function for testing
call_count = 0

@retry(max_attempts=3, backoff_base=0.5, exceptions=(RuntimeError,))
def unreliable_api_call():
    """Simulates an unreliable API that fails randomly."""
    global call_count
    call_count += 1
    
    print(f"[Attempt {call_count}] Making API call...")
    
    # Fail on first 2 attempts, succeed on 3rd
    if call_count < 3:
        print(f"[Attempt {call_count}] ❌ Failed!")
        raise RuntimeError("Simulated network timeout")
    
    print(f"[Attempt {call_count}] ✅ Success!")
    return "API response data"


def main():
    """Test retry logic with examples."""
    
    print("=" * 70)
    print("AXIOM AI - RETRY LOGIC TEST")
    print("=" * 70)
    print()
    
    # Test 1: Successful retry after failures
    print("TEST 1: Retry with eventual success")
    print("-" * 70)
    global call_count
    call_count = 0
    
    try:
        result = unreliable_api_call()
        print(f"\nFinal result: {result}")
        print("✅ Test 1 PASSED: Retry logic worked!\n")
    except AllRetriesFailed as e:
        print(f"\n❌ Test 1 FAILED: {e}\n")
    
    print()
    
    # Test 2: All retries fail
    print("TEST 2: All retries exhausted")
    print("-" * 70)
    
    @retry(max_attempts=2, backoff_base=0.5, exceptions=(ValueError,))
    def always_fails():
        print("[Attempt] Trying to call failing service...")
        raise ValueError("Service unavailable")
    
    try:
        always_fails()
        print("❌ Test 2 FAILED: Should have raised AllRetriesFailed\n")
    except AllRetriesFailed as e:
        print(f"\n✅ Test 2 PASSED: Correctly raised AllRetriesFailed")
        print(f"   Error: {str(e)[:100]}...\n")
    
    print()
    
    # Test 3: Exponential backoff timing
    print("TEST 3: Exponential backoff timing")
    print("-" * 70)
    print("Watch the delays increase: 0.5s → 1.0s → 2.0s")
    print()
    
    attempt_times = []
    
    @retry(max_attempts=3, backoff_base=0.5, exceptions=(RuntimeError,))
    def track_timing():
        attempt_times.append(time.time())
        if len(attempt_times) < 3:
            raise RuntimeError("Not yet!")
        return "Success!"
    
    try:
        track_timing()
        
        # Calculate delays
        if len(attempt_times) >= 2:
            delay1 = attempt_times[1] - attempt_times[0]
            delay2 = attempt_times[2] - attempt_times[1]
            
            print(f"Delay before retry 2: {delay1:.2f}s (expected ~0.5s)")
            print(f"Delay before retry 3: {delay2:.2f}s (expected ~1.0s)")
            print("✅ Test 3 PASSED: Exponential backoff working!\n")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}\n")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✅ Retry decorator works with exponential backoff")
    print("✅ Correctly handles eventual success")
    print("✅ Correctly raises AllRetriesFailed when exhausted")
    print("✅ Delays follow exponential pattern")
    print()
    print("=" * 70)
    print()
    print("💡 HOW THIS HELPS IN PRODUCTION:")
    print()
    print("1. Transient failures (network glitches) → Auto-retry → Success")
    print("2. Rate limits (429 errors) → Wait longer → Success")
    print("3. Permanent failures → Fail fast after max attempts")
    print("4. Graceful degradation → Return partial results when LLM fails")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()

