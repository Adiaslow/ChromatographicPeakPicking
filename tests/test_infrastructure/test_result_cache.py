# tests/test_infrastructure/test_result_cache.py

import pytest
from src.chromatographicpeakpicking.infrastructure.caching.result_cache import ResultCache

def test_result_cache_initialization():
    cache = ResultCache()
    assert cache is not None

def test_result_cache_set_get():
    cache = ResultCache()
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

def test_result_cache_invalidate():
    cache = ResultCache()
    cache.set("key1", "value1")
    cache.invalidate("key1")
    assert cache.get("key1") is None
