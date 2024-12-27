# tests/test_analyzers/test_peak_analyzer.py
import pytest
import numpy as np
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

def test_analyze_peak():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([10, 20, 30, 40, 50])
    chromatogram = Chromatogram(time=time, intensity=intensity)
    assert chromatogram.time.tolist() == [0, 1, 2, 3, 4]
    assert chromatogram.intensity.tolist() == [10, 20, 30, 40, 50]
