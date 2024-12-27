# tests/test_baseline_correctors/test_swm.py
import pytest
from src.chromatographicpeakpicking.analysis.baseline.swm import SWM, SWMConfig
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram
import numpy as np

def test_swm_initialization():
    corrector = SWM()
    assert corrector is not None

def test_swm_correction():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([1, 2, 3, 4, 5])
    chromatogram = Chromatogram(time=time, intensity=intensity)

    corrector = SWM()
    result = corrector.correct(chromatogram)
    assert result is not None
    assert len(result.intensity) == len(intensity)
