# tests/test_core/test_peptide.py
import pytest
from src.chromatographicpeakpicking.core.domain.peptide import Peptide
from src.chromatographicpeakpicking.core.domain.building_block import BuildingBlock

def test_peptide_initialization():
    sequence = [BuildingBlock('A', 89.09), BuildingBlock('C', 121.15)]
    peptide = Peptide(sequence=sequence)
    assert peptide.sequence == sequence
    assert peptide.length == 2
    assert peptide.mass == sum(block.mass for block in sequence)

def test_peptide_with_retention_time():
    sequence = [BuildingBlock('A', 89.09), BuildingBlock('C', 121.15)]
    peptide = Peptide(sequence=sequence)
    new_peptide = peptide.with_retention_time(5.5)
    assert new_peptide.retention_time == 5.5
    assert new_peptide.sequence == sequence

def test_peptide_with_peak_metrics():
    sequence = [BuildingBlock('A', 89.09), BuildingBlock('C', 121.15)]
    peptide = Peptide(sequence=sequence)
    new_peptide = peptide.with_peak_metrics(area=200.0, height=500.0)
    assert new_peptide.peak_area == 200.0
    assert new_peptide.peak_height == 500.0

def test_peptide_with_metadata():
    sequence = [BuildingBlock('A', 89.09), BuildingBlock('C', 121.15)]
    peptide = Peptide(sequence=sequence)
    new_peptide = peptide.with_metadata(source="experiment_1")
    assert new_peptide.metadata["source"] == "experiment_1"

def test_peptide_get_sequence_string():
    sequence = [BuildingBlock('A', 89.09), BuildingBlock('C', 121.15)]
    peptide = Peptide(sequence=sequence)
    assert peptide.get_sequence_string(separator="-") == "A-C"
