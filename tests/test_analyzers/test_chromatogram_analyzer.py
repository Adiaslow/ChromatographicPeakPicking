# tests/test_analyzers/test_chromatogram_analyzer.py
import pytest
import numpy as np
from src.chromatographicpeakpicking.analyzers.chromatogram_analyzer import ChromatogramAnalyzer, ChromatogramAnalyzerConfig
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

@pytest.fixture
def chroma_config():
    return ChromatogramAnalyzerConfig()

def test_analyze_chromatogram(chroma_config):
    analyzer = ChromatogramAnalyzer(config=chroma_config)
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([10, 20, 30, 40, 50])
    chromatogram = Chromatogram(time=time, intensity=intensity)
    result = analyzer.analyze_chromatogram(chromatogram)
    assert result is not None
    assert 'noise_level' in result.metadata
    assert 'signal_to_noise' in result.metadata
    assert 'baseline_mean' in result.metadata
    assert 'total_area' in result.metadata

def test_configure(chroma_config):
    analyzer = ChromatogramAnalyzer()
    validation_result = analyzer.configure(chroma_config)
    assert validation_result.is_valid
