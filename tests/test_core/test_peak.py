# tests/test_core/test_peak.py
import pytest
from src.chromatographicpeakpicking.core.domain.peak import Peak
import numpy as np

def test_peak_initialization():
    peak = Peak(
        apex_time=5.0,
        apex_intensity=100.0,
        start_time=2.0,
        end_time=8.0,
        height=100.0,
        area=400.0
    )
    assert peak.apex_time == 5.0
    assert peak.apex_intensity == 100.0
    assert peak.start_time == 2.0
    assert peak.end_time == 8.0
    assert peak.height == 100.0
    assert peak.area == 400.0

def test_peak_update_gaussian_fit():
    peak = Peak(
        apex_time=5.0,
        apex_intensity=100.0,
        start_time=2.0,
        end_time=8.0,
        height=100.0,
        area=400.0
    )
    gaussian_params = {'mean': 5.0, 'sigma': 1.0, 'amplitude': 100.0}
    new_peak = peak.with_gaussian_fit(gaussian_params)
    assert new_peak.gaussian_params == gaussian_params
    assert new_peak.apex_time == peak.apex_time  # Ensure other attributes are the same

def test_peak_width():
    peak = Peak(
        apex_time=5.0,
        apex_intensity=100.0,
        start_time=2.0,
        end_time=8.0,
        height=100.0,
        area=400.0
    )
    assert peak.width == 6.0  # end_time - start_time

def test_peak_symmetry():
    peak = Peak(
        apex_time=5.0,
        apex_intensity=100.0,
        start_time=2.0,
        end_time=8.0,
        height=100.0,
        area=400.0,
        asymmetry_factor=1.5
    )
    assert peak.symmetry == 1 / 1.5

def test_peak_with_raw_data():
    raw_times = np.array([1, 2, 3, 4, 5])
    raw_intensities = np.array([10, 20, 30, 40, 50])
    peak = Peak(
        apex_time=5.0,
        apex_intensity=100.0,
        start_time=2.0,
        end_time=8.0,
        height=100.0,
        area=400.0,
        raw_times=raw_times,
        raw_intensities=raw_intensities
    )
    assert np.array_equal(peak.raw_times, raw_times)
    assert np.array_equal(peak.raw_intensities, raw_intensities)
