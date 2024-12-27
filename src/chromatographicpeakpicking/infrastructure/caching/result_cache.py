# src/chromatographicpeakpicking/infrastructure/caching/result_cache.py
from typing import Generic, TypeVar, Optional, Dict
from datetime import datetime, timedelta

T = TypeVar('T')

class ResultCache(Generic[T]):
    """Generic cache for analysis results."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, T] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[T]:
        """Get a cached result.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        timestamp = self._timestamps[key]
        if datetime.now() - timestamp > self._ttl:
            self.invalidate(key)
            return None

        return self._cache[key]

    def set(self, key: str, value: T) -> None:
        """Cache a result.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def invalidate(self, key: str) -> None:
        """Invalidate a cached result.

        Args:
            key: Cache key to invalidate
        """
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._timestamps.clear()
