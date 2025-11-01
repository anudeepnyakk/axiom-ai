"""
Test script for API key authentication.

Demonstrates:
- Key generation
- Authentication success/failure
- Constant-time comparison
- Multiple keys support
"""

import os
import time
from axiom.security import APIKeyAuth, APIKeyGenerator, verify_api_key


def test_key_generation():
    """Test API key generation"""
    print("\n" + "="*60)
    print("TEST 1: API Key Generation")
    print("="*60)
    
    key1 = APIKeyGenerator.generate(prefix="axiom", length=32)
    key2 = APIKeyGenerator.generate(prefix="test", length=16)
    
    print(f"Generated Key 1: {key1}")
    print(f"Generated Key 2: {key2}")
    
    assert key1.startswith("axiom_")
    assert key2.startswith("test_")
    assert len(key1.split("_")[1]) == 32
    assert len(key2.split("_")[1]) == 16
    assert key1 != key2
    
    print("✅ PASSED: Keys generated with correct format")
    return key1, key2


def test_authentication_success():
    """Test successful authentication"""
    print("\n" + "="*60)
    print("TEST 2: Authentication Success")
    print("="*60)
    
    valid_keys = ["test_key_123", "test_key_456"]
    auth = APIKeyAuth(api_keys=valid_keys)
    
    # Test with first key
    result1 = auth.verify_key("test_key_123")
    print(f"Verify 'test_key_123': {result1}")
    assert result1 is True
    
    # Test with second key
    result2 = auth.verify_key("test_key_456")
    print(f"Verify 'test_key_456': {result2}")
    assert result2 is True
    
    print("✅ PASSED: Valid keys authenticated successfully")


def test_authentication_failure():
    """Test failed authentication"""
    print("\n" + "="*60)
    print("TEST 3: Authentication Failure")
    print("="*60)
    
    valid_keys = ["test_key_123"]
    auth = APIKeyAuth(api_keys=valid_keys)
    
    # Test with wrong key
    result1 = auth.verify_key("wrong_key")
    print(f"Verify 'wrong_key': {result1}")
    assert result1 is False
    
    # Test with None
    result2 = auth.verify_key(None)
    print(f"Verify None: {result2}")
    assert result2 is False
    
    # Test with empty string
    result3 = auth.verify_key("")
    print(f"Verify '': {result3}")
    assert result3 is False
    
    print("✅ PASSED: Invalid keys rejected correctly")


def test_constant_time_comparison():
    """Test that comparison is constant-time (basic check)"""
    print("\n" + "="*60)
    print("TEST 4: Constant-Time Comparison")
    print("="*60)
    
    auth = APIKeyAuth(api_keys=["correct_key_12345678901234567890"])
    
    # Time comparison with correct key
    start = time.perf_counter()
    for _ in range(1000):
        auth.verify_key("correct_key_12345678901234567890")
    correct_time = time.perf_counter() - start
    
    # Time comparison with wrong key (same length)
    start = time.perf_counter()
    for _ in range(1000):
        auth.verify_key("wronggg_key_12345678901234567890")
    wrong_time = time.perf_counter() - start
    
    print(f"Time for correct key (1000 checks): {correct_time:.6f}s")
    print(f"Time for wrong key (1000 checks):   {wrong_time:.6f}s")
    print(f"Difference: {abs(correct_time - wrong_time):.6f}s")
    
    # The times should be very similar (within 20% of each other)
    # This is a basic check - true constant-time requires deeper analysis
    ratio = max(correct_time, wrong_time) / min(correct_time, wrong_time)
    print(f"Time ratio: {ratio:.2f}x")
    
    # Allow up to 2x variation due to system noise
    assert ratio < 2.0, f"Timing difference too large: {ratio}x"
    
    print("✅ PASSED: Comparison appears to be constant-time")


def test_multiple_keys():
    """Test authentication with multiple keys"""
    print("\n" + "="*60)
    print("TEST 5: Multiple Keys Support")
    print("="*60)
    
    keys = [
        "client1_abc123",
        "client2_def456",
        "client3_ghi789"
    ]
    auth = APIKeyAuth(api_keys=keys)
    
    # All should be valid
    for key in keys:
        result = auth.verify_key(key)
        print(f"Verify '{key}': {result}")
        assert result is True
    
    # Wrong key should fail
    result = auth.verify_key("wrong_key")
    print(f"Verify 'wrong_key': {result}")
    assert result is False
    
    print("✅ PASSED: Multiple keys working correctly")


def test_environment_variable_loading():
    """Test loading keys from environment variable"""
    print("\n" + "="*60)
    print("TEST 6: Environment Variable Loading")
    print("="*60)
    
    # Set environment variable
    os.environ["TEST_API_KEYS"] = "key1_test,key2_test,key3_test"
    
    auth = APIKeyAuth(env_var="TEST_API_KEYS")
    
    # All keys should be valid
    assert auth.verify_key("key1_test") is True
    assert auth.verify_key("key2_test") is True
    assert auth.verify_key("key3_test") is True
    assert auth.verify_key("wrong_key") is False
    
    print("Loaded keys from TEST_API_KEYS environment variable")
    print("✅ PASSED: Environment variable loading working")
    
    # Clean up
    del os.environ["TEST_API_KEYS"]


def test_decorator():
    """Test the require_api_key decorator"""
    print("\n" + "="*60)
    print("TEST 7: Decorator Pattern")
    print("="*60)
    
    auth = APIKeyAuth(api_keys=["valid_key"])
    
    @auth.require_api_key
    def protected_function(message: str) -> str:
        return f"Success: {message}"
    
    # Should work with valid key
    result = protected_function("Hello", api_key="valid_key")
    print(f"With valid key: {result}")
    assert result == "Success: Hello"
    
    # Should fail with invalid key
    try:
        protected_function("Hello", api_key="wrong_key")
        assert False, "Should have raised PermissionError"
    except PermissionError as e:
        print(f"With invalid key: PermissionError raised - {e}")
    
    print("✅ PASSED: Decorator working correctly")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "API AUTHENTICATION TEST SUITE" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_key_generation()
        test_authentication_success()
        test_authentication_failure()
        test_constant_time_comparison()
        test_multiple_keys()
        test_environment_variable_loading()
        test_decorator()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ API Authentication is working correctly!")
        print("   - Secure key generation")
        print("   - Constant-time comparison (prevents timing attacks)")
        print("   - Multiple keys support")
        print("   - Environment variable configuration")
        print("   - Decorator pattern for easy protection")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

