# src/chromatographicpeakpicking/core/singletons/cache_singleton.py
"""
Module: cache_singleton

This module defines the CacheSingleton class that follows the Singleton design pattern
to store and manage cached objects.

Design Patterns:
    - Singleton Pattern: Ensures that a class has only one instance and provides a global point of access to it.

Rationale:
    - Efficiency: A single instance of the cache can be used throughout the application, reducing memory usage and improving access times.
    - Consistency: Ensures that all parts of the application are using the same cache, preventing inconsistencies.
    - Simplicity: Simplifies access to the cache by providing a global point of access.
"""

from typing import Dict, Any, Optional, TypeVar, Type
from threading import Lock

# Define a type variable bound to the CacheSingleton class
T = TypeVar('T', bound='CacheSingleton')

class CacheSingleton:
    """
    A singleton cache for storing and managing cached objects.

    This class encapsulates the logic for caching objects,
    providing methods to get, set, remove, and clear cached objects.
    """

    _instance = None
    _lock: Lock = Lock()

    def __new__(cls) -> 'CacheSingleton':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(CacheSingleton, cls).__new__(cls)
                    object.__setattr__(instance, 'cache', {})
                    cls._instance = instance
        return cls._instance

    def get(self, key: str) -> Any:
        """
        Retrieve an object from the cache.

        Args:
            key (str): The key of the object to retrieve.

        Returns:
            Any: The cached object. Raises KeyError if the key does not exist.

        Raises:
            KeyError: If the key does not exist in the cache.
        """
        if key not in self.__dict__['cache']:
            raise KeyError(f"No object found in cache for key: {key}")
        return self.__dict__['cache'][key]

    def set(self, key: str, value: Any) -> None:
        """
        Store an object in the cache.

        Args:
            key (str): The key to store the object under.
            value (Any): The object to store in the cache.
        """
        self.__dict__['cache'][key] = value

    def remove(self, key: str) -> None:
        """
        Remove an object from the cache.

        Args:
            key (str): The key of the object to remove.
        """
        if key in self.__dict__['cache']:
            del self.__dict__['cache'][key]

    def clear(self) -> None:
        """
        Clear all objects from the cache.
        """
        self.__dict__['cache'].clear()
