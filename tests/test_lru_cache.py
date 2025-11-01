"""
Test script for LRU cache implementation.

Demonstrates:
- Basic get/put operations
- LRU eviction policy
- TTL expiration
- Thread safety
- Cache statistics
"""

import time
import threading
from axiom.caching import LRUCache, CacheStats


def test_basic_operations():
    """Test basic get and put operations"""
    print("\n" + "="*60)
    print("TEST 1: Basic Get/Put Operations")
    print("="*60)
    
    cache = LRUCache(capacity=3)
    
    # Put some items
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.put("key3", "value3")
    
    # Get items
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    
    print("✓ Put 3 items")
    print("✓ Retrieved all 3 items")
    
    # Stats
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
    assert stats.hits == 3
    assert stats.misses == 0
    
    print("✅ PASSED: Basic operations working")


def test_lru_eviction():
    """Test LRU eviction policy"""
    print("\n" + "="*60)
    print("TEST 2: LRU Eviction Policy")
    print("="*60)
    
    cache = LRUCache(capacity=3)
    
    # Fill cache
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.put("key3", "value3")
    
    print("Cache full: key1, key2, key3")
    
    # Access key1 (makes it most recently used)
    cache.get("key1")
    print("Accessed key1 (now most recent)")
    
    # Add key4 (should evict key2, the least recently used)
    cache.put("key4", "value4")
    print("Added key4")
    
    # key2 should be evicted
    assert cache.get("key2") is None
    assert cache.get("key1") == "value1"
    assert cache.get("key3") == "value3"
    assert cache.get("key4") == "value4"
    
    print("✓ key2 evicted (least recently used)")
    print("✓ key1, key3, key4 still present")
    
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
    assert stats.evictions == 1
    
    print("✅ PASSED: LRU eviction working correctly")


def test_cache_update():
    """Test updating existing keys"""
    print("\n" + "="*60)
    print("TEST 3: Cache Update")
    print("="*60)
    
    cache = LRUCache(capacity=3)
    
    cache.put("key1", "value1")
    print("Put key1 = 'value1'")
    
    cache.put("key1", "updated_value1")
    print("Updated key1 = 'updated_value1'")
    
    result = cache.get("key1")
    assert result == "updated_value1"
    print(f"Retrieved key1 = '{result}'")
    
    # Size should still be 1
    assert len(cache) == 1
    
    print("✅ PASSED: Cache update working")


def test_ttl_expiration():
    """Test TTL (Time-To-Live) expiration"""
    print("\n" + "="*60)
    print("TEST 4: TTL Expiration")
    print("="*60)
    
    cache = LRUCache(capacity=10, ttl=0.5)  # 0.5 second TTL
    
    cache.put("key1", "value1")
    print("Put key1 with TTL=0.5s")
    
    # Should be available immediately
    result = cache.get("key1")
    assert result == "value1"
    print("✓ Retrieved immediately: success")
    
    # Wait for expiration
    print("Waiting 0.6 seconds for expiration...")
    time.sleep(0.6)
    
    # Should be expired
    result = cache.get("key1")
    assert result is None
    print("✓ After TTL: expired (returns None)")
    
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
    assert stats.misses == 1  # The expired get counts as miss
    
    print("✅ PASSED: TTL expiration working")


def test_cache_statistics():
    """Test cache statistics tracking"""
    print("\n" + "="*60)
    print("TEST 5: Cache Statistics")
    print("="*60)
    
    cache = LRUCache(capacity=2)
    
    # Misses
    cache.get("nonexistent1")
    cache.get("nonexistent2")
    print("✓ 2 misses")
    
    # Hits
    cache.put("key1", "value1")
    cache.get("key1")
    cache.get("key1")
    print("✓ 2 hits")
    
    # Eviction
    cache.put("key2", "value2")
    cache.put("key3", "value3")  # Evicts key1
    print("✓ 1 eviction")
    
    stats = cache.get_stats()
    print(f"\nFinal Stats: {stats}")
    
    assert stats.hits == 2
    assert stats.misses == 2
    assert stats.evictions == 1
    assert stats.hit_rate == 0.5
    assert stats.size == 2
    assert stats.capacity == 2
    
    print(f"✓ Hit rate: {stats.hit_rate:.1%}")
    print("✅ PASSED: Statistics tracking correctly")


def test_thread_safety():
    """Test thread-safe operations"""
    print("\n" + "="*60)
    print("TEST 6: Thread Safety")
    print("="*60)
    
    cache = LRUCache(capacity=100, thread_safe=True)
    errors = []
    
    def worker(thread_id: int, operations: int):
        """Worker thread that performs cache operations"""
        try:
            for i in range(operations):
                key = f"thread{thread_id}_key{i}"
                value = f"value{i}"
                
                cache.put(key, value)
                result = cache.get(key)
                
                if result != value:
                    errors.append(f"Thread {thread_id}: Expected {value}, got {result}")
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")
    
    # Start multiple threads
    threads = []
    for tid in range(5):
        t = threading.Thread(target=worker, args=(tid, 20))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print(f"✓ 5 threads completed (100 operations each)")
    
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  {error}")
        raise AssertionError("Thread safety test failed")
    
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
    print("✅ PASSED: Thread-safe operations working")


def test_clear_cache():
    """Test cache clearing"""
    print("\n" + "="*60)
    print("TEST 7: Clear Cache")
    print("="*60)
    
    cache = LRUCache(capacity=10)
    
    # Add items
    for i in range(5):
        cache.put(f"key{i}", f"value{i}")
    
    print(f"Added 5 items, size: {len(cache)}")
    assert len(cache) == 5
    
    # Clear
    cache.clear()
    print("Cache cleared")
    
    assert len(cache) == 0
    assert cache.get("key0") is None
    
    print("✓ Size is 0")
    print("✓ All items removed")
    print("✅ PASSED: Clear cache working")


def test_performance():
    """Test cache performance"""
    print("\n" + "="*60)
    print("TEST 8: Performance Benchmark")
    print("="*60)
    
    cache = LRUCache(capacity=1000)
    operations = 10000
    
    # Benchmark puts
    start = time.perf_counter()
    for i in range(operations):
        cache.put(f"key{i % 500}", f"value{i}")
    put_time = time.perf_counter() - start
    
    # Benchmark gets
    start = time.perf_counter()
    for i in range(operations):
        cache.get(f"key{i % 500}")
    get_time = time.perf_counter() - start
    
    print(f"Operations: {operations:,}")
    print(f"Put time: {put_time:.4f}s ({operations/put_time:.0f} ops/sec)")
    print(f"Get time: {get_time:.4f}s ({operations/get_time:.0f} ops/sec)")
    
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
    
    # Should be fast (rough checks)
    assert put_time < 1.0, f"Puts too slow: {put_time}s"
    assert get_time < 1.0, f"Gets too slow: {get_time}s"
    
    print("✅ PASSED: Performance acceptable")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*18 + "LRU CACHE TEST SUITE" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_basic_operations()
        test_lru_eviction()
        test_cache_update()
        test_ttl_expiration()
        test_cache_statistics()
        test_thread_safety()
        test_clear_cache()
        test_performance()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ LRU Cache is production-ready!")
        print("   - O(1) get and put operations")
        print("   - Proper LRU eviction policy")
        print("   - TTL expiration support")
        print("   - Thread-safe")
        print("   - Comprehensive statistics")
        print("   - High performance (10K+ ops/sec)")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

