# src/chromatographicpeakpicking/infrastructure/caching/result_cache.py

"""
Cache for storing analysis results.
"""

class ResultCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        """
        Retrieve a result from the cache.

        Args:
            key: The key for the cached result.
        """
        return self.cache.get(key)

    def set(self, key, value):
        """
        Store a result in the cache.

        Args:
            key: The key for the result.
            value: The result to store.
        """
        self.cache[key] = value

    def invalidate(self, key):
        """
        Invalidate a cached result.

        Args:
            key: The key for the result to invalidate.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clear the entire cache.
        """
        self.cache.clear()
