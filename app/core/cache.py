"""
Simple in-memory TTL cache implementation.

Provides a thread-safe cache with time-to-live (TTL) expiration and size limits.
"""
import time
from threading import Lock
from typing import Any, Dict, Optional


class TTLCache:
    """
    Time-to-live cache with maximum size limit.
    
    Entries expire after a specified TTL. When max size is reached,
    oldest entries are evicted using LRU-like behavior.
    """
    
    def __init__(self, ttl: int = 3600, max_size: int = 100):
        """
        Initialize TTL cache.
        
        Args:
            ttl: Time-to-live in seconds for cache entries
            max_size: Maximum number of entries in cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if exists and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            # Update access time for LRU
            entry["accessed_at"] = time.time()
            return entry["value"]
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Evict oldest if at max size
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_oldest()
            
            current_time = time.time()
            self._cache[key] = {
                "value": value,
                "expires_at": current_time + self.ttl,
                "accessed_at": current_time,
            }
    
    def _evict_oldest(self) -> None:
        """Evict the least recently accessed entry."""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]["accessed_at"]
        )
        del self._cache[oldest_key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            # Clean expired entries
            current_time = time.time()
            expired_keys = [
                k for k, v in self._cache.items()
                if current_time > v["expires_at"]
            ]
            for k in expired_keys:
                del self._cache[k]
            
            return len(self._cache)


# Global cache instance
cache = TTLCache()
