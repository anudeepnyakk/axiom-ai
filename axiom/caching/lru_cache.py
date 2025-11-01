"""
LRU (Least Recently Used) Cache Implementation

A production-ready LRU cache for embedding results.

Features:
- O(1) get and put operations
- Thread-safe (optional)
- Configurable capacity
- Cache statistics (hits, misses, evictions)
- TTL (Time-To-Live) support
"""

import time
import logging
import hashlib
from collections import OrderedDict
from typing import Any, Optional, Callable
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    capacity: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def __str__(self) -> str:
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"evictions={self.evictions}, hit_rate={self.hit_rate:.2%}, "
            f"size={self.size}/{self.capacity})"
        )


class LRUCache:
    """
    Thread-safe LRU Cache with TTL support.
    
    Uses OrderedDict for O(1) access and LRU eviction.
    """
    
    def __init__(
        self,
        capacity: int = 1000,
        ttl: Optional[float] = None,
        thread_safe: bool = True
    ):
        """
        Initialize LRU cache.
        
        Args:
            capacity: Maximum number of items in cache
            ttl: Time-to-live in seconds (None = no expiration)
            thread_safe: Whether to use locks for thread safety
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.ttl = ttl
        self.thread_safe = thread_safe
        
        # Cache storage: key -> (value, timestamp)
        self._cache: OrderedDict = OrderedDict()
        
        # Thread safety
        self._lock = Lock() if thread_safe else None
        
        # Statistics
        self._stats = CacheStats(capacity=capacity)
        
        logger.info(
            f"LRUCache initialized: capacity={capacity}, ttl={ttl}, thread_safe={thread_safe}"
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if self._lock:
            with self._lock:
                return self._get_internal(key)
        else:
            return self._get_internal(key)
    
    def _get_internal(self, key: str) -> Optional[Any]:
        """Internal get implementation (not thread-safe)."""
        if key not in self._cache:
            self._stats.misses += 1
            return None
        
        value, timestamp = self._cache[key]
        
        # Check TTL expiration
        if self.ttl and (time.time() - timestamp) > self.ttl:
            # Expired - remove and return None
            del self._cache[key]
            self._stats.size = len(self._cache)
            self._stats.misses += 1
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        self._stats.hits += 1
        return value
    
    def put(self, key: str, value: Any) -> None:
        """
        Put value into cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if self._lock:
            with self._lock:
                self._put_internal(key, value)
        else:
            self._put_internal(key, value)
    
    def _put_internal(self, key: str, value: Any) -> None:
        """Internal put implementation (not thread-safe)."""
        timestamp = time.time()
        
        if key in self._cache:
            # Update existing entry
            self._cache[key] = (value, timestamp)
            self._cache.move_to_end(key)
        else:
            # New entry
            if len(self._cache) >= self.capacity:
                # Evict least recently used (first item)
                self._cache.popitem(last=False)
                self._stats.evictions += 1
            
            self._cache[key] = (value, timestamp)
        
        self._stats.size = len(self._cache)
    
    def clear(self) -> None:
        """Clear all items from cache."""
        if self._lock:
            with self._lock:
                self._cache.clear()
                self._stats.size = 0
        else:
            self._cache.clear()
            self._stats.size = 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        if self._lock:
            with self._lock:
                return CacheStats(
                    hits=self._stats.hits,
                    misses=self._stats.misses,
                    evictions=self._stats.evictions,
                    size=len(self._cache),
                    capacity=self.capacity
                )
        else:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                size=len(self._cache),
                capacity=self.capacity
            )
    
    def __len__(self) -> int:
        """Return number of items in cache."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache (doesn't update LRU order)."""
        return key in self._cache


class CachedEmbeddingWrapper:
    """
    Wraps an embedding generator with LRU caching.
    
    Automatically hashes input text to create cache keys.
    """
    
    def __init__(
        self,
        embedding_generator,
        cache_capacity: int = 1000,
        ttl: Optional[float] = 3600  # 1 hour default
    ):
        """
        Initialize cached embedding wrapper.
        
        Args:
            embedding_generator: The underlying embedding generator
            cache_capacity: Maximum cache size
            ttl: Time-to-live for cached embeddings (seconds)
        """
        self.embedding_generator = embedding_generator
        self.cache = LRUCache(capacity=cache_capacity, ttl=ttl)
        self._logger = logging.getLogger(__name__)
        
        self._logger.info(
            f"CachedEmbeddingWrapper initialized: capacity={cache_capacity}, ttl={ttl}"
        )
    
    def embed_batch(self, chunks):
        """
        Generate embeddings with caching.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            List of embeddings (cached or freshly generated)
        """
        results = []
        uncached_chunks = []
        uncached_indices = []
        
        # Check cache for each chunk
        for i, chunk in enumerate(chunks):
            cache_key = self._get_cache_key(chunk.text)
            cached_embedding = self.cache.get(cache_key)
            
            if cached_embedding is not None:
                results.append(cached_embedding)
            else:
                results.append(None)  # Placeholder
                uncached_chunks.append(chunk)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached chunks
        if uncached_chunks:
            fresh_embeddings = self.embedding_generator.embed_batch(uncached_chunks)
            
            # Cache and insert into results
            for idx, embedding in zip(uncached_indices, fresh_embeddings):
                cache_key = self._get_cache_key(chunks[idx].text)
                self.cache.put(cache_key, embedding)
                results[idx] = embedding
        
        # Log cache statistics
        stats = self.cache.get_stats()
        self._logger.info(
            f"Embedding cache: {stats.hits} hits, {stats.misses} misses, "
            f"hit rate {stats.hit_rate:.2%}"
        )
        
        return results
    
    @staticmethod
    def _get_cache_key(text: str) -> str:
        """Generate cache key from text using SHA-256."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self._logger.info("Embedding cache cleared")

