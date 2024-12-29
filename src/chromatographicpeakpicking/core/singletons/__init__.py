# src/chromatographicpeakpicking/core/singletons/__init__.py
"""
This module aggregates and re-exports singleton instances of key components used in
"""
from .cache_singleton import CacheSingleton

__all__ = [
    'CacheSingleton'
]
