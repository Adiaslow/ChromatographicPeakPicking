# tests/test_core/test_building_block.py
import pytest
from src.chromatographicpeakpicking.core.domain.building_block import BuildingBlock

def test_building_block_initialization():
    block = BuildingBlock(name="TestBlock", mass=123)
    assert block.name == "TestBlock"
    assert block.mass == 123
