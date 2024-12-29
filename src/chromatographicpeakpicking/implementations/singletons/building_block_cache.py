# src/chromatographicpeakpicking/implementations/singletons/building_block_cache.py
"""
Module: building_block_cache

This module defines the BuildingBlockCache class, which is a singleton cache for storing and
managing BuildingBlock instances. It extends the CacheSingleton.

Design Patterns:
    - Singleton Pattern: Ensures that a class has only one instance and provides a global point of access to it.
    - Prototype Pattern: Used to create new objects by copying an existing object (the prototype).

Rationale:
    - Efficiency: A single instance of the cache can be used throughout the application, reducing memory usage and improving access times.
    - Consistency: Ensures that all parts of the application are using the same cache, preventing inconsistencies.
    - Simplicity: Simplifies access to the cache by providing a global point of access.
"""

from typing import Optional
from ...core.singletons.cache_singleton import CacheSingleton
from ...core.prototypes.building_block import BuildingBlock

class BuildingBlockCache(CacheSingleton):
    """
    A cache singleton for storing and managing BuildingBlock instances.

    This class encapsulates the logic for caching BuildingBlock instances,
    providing methods to get, set, remove, and clear cached objects.
    """

    _instance: Optional['BuildingBlockCache'] = None  # Singleton instance

    def __new__(cls) -> 'BuildingBlockCache':
            if cls._instance is None:
                with cls._lock:
                    if cls._instance is None:
                        instance = super(BuildingBlockCache, cls).__new__(cls)
                        instance.cache = {}  # Initialize cache on instance, not class
                        cls._instance = instance
            if cls._instance is not None:
                return cls._instance
            raise RuntimeError("Failed to create singleton instance")  # Defensive check

    def get(self, key: str) -> BuildingBlock:
        """
        Retrieve a BuildingBlock from the cache.

        Args:
            key (str): The key of the BuildingBlock to retrieve.

        Returns:
            BuildingBlock: The cached BuildingBlock. Raises KeyError if key does not exist.

        Raises:
            KeyError: If the key does not exist in the cache.
        """
        return super().get(key)

    def set(self, key: str, value: BuildingBlock) -> None:
        """
        Store a BuildingBlock in the cache.

        Args:
            key (str): The key to store the BuildingBlock under.
            value (BuildingBlock): The BuildingBlock to store in the cache.
        """
        super().set(key, value)

    def remove(self, key: str) -> None:
        """
        Remove a BuildingBlock from the cache.

        Args:
            key (str): The key of the BuildingBlock to remove.
        """
        super().remove(key)

    def clear(self) -> None:
        """
        Clear all BuildingBlocks from the cache.
        """
        super().clear()
