# tests/test_baseline_correctors/test_aals.py
import pytest
import numpy as np
from src.chromatographicpeakpicking.analysis.baseline.aals import AALSCorrector
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

def test_aals_correction():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([1, 2, 3, 4, 5])
    chromatogram = Chromatogram(time=time, intensity=intensity)

    corrector = AALSCorrector()
    result = corrector.correct(chromatogram)
    assert result is not None
    assert len(result.intensity) == len(intensity)
    assert result.baseline is not None
    assert len(result.baseline) == len(intensity)
    assert np.allclose(result.intensity + result.baseline, intensity)
