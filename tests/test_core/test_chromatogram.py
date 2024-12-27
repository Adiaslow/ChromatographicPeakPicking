# tests/test_core/test_chromatogram.py
import pytest
import numpy as np
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

def test_chromatogram_initialization():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([10, 20, 30, 40, 50])
    chromatogram = Chromatogram(time=time, intensity=intensity)
    assert chromatogram.time.tolist() == [0, 1, 2, 3, 4]
    assert chromatogram.intensity.tolist() == [10, 20, 30, 40, 50]

def test_chromatogram_add_data():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([10, 20, 30, 40, 50])
    chromatogram = Chromatogram(time=time, intensity=intensity)

    # Assuming add_data method is used to add a new time-intensity pair
    new_time = 5
    new_intensity = 60

    # Create a new chromatogram with the added data
    new_chromatogram = Chromatogram(
        time=np.append(chromatogram.time, new_time),
        intensity=np.append(chromatogram.intensity, new_intensity)
    )

    assert new_chromatogram.time.tolist() == [0, 1, 2, 3, 4, 5]
    assert new_chromatogram.intensity.tolist() == [10, 20, 30, 40, 50, 60]
