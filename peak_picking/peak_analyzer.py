from dataclasses import dataclass
import numpy as np
from scipy.signal import peak_widths
from scipy.integrate import trapz
from typing import Tuple

from .peak import Peak
from .chromatogram import Chromatogram

@dataclass
class PeakAnalyzer:
    """Class for analyzing peaks in chromatograms.

    Attributes:
        None

    Methods:
        analyze_peak: Analyzes a peak in a chromatogram
        _find_peak_boundaries: Finds the boundaries of a peak
        _calculate_peak_width: Calculates the width of a peak
        _calculate_peak_area: Calculates the area of a peak
        _calculate_peak_symmetry: Calculates the symmetry of a peak
        _calculate_peak_skewness: Calculates the skewness of a peak
    """
    @staticmethod
    def analyze_peak(
        peak: Peak,
        chromatogram: Chromatogram
    ) -> Peak:
        """Analyzes a peak in a chromatogram.

        Args:
            peak (Peak): peak to be scored
            chromatogram (Chromatogram): chromatogram to be analyzed

        Returns:
            Peak:
        """
        x = chromatogram.x
        y = chromatogram.y_corrected
        peak = PeakAnalyzer._calculate_peak_width(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_area(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_symmetry(y, peak)
        peak = PeakAnalyzer._calculate_peak_skewness(y, peak)
        peak = PeakAnalyzer._calculate_peak_score(peak)
        return peak

    @staticmethod
    def _find_peak_boundaries(
        x: np.ndarray,
        y: np.ndarray,
        peak: Peak
    ) -> Peak:
        """Finds the boundaries of a peak.

        Args:
            y (np.ndarray): intensity values of the chromatogram
            peak (Peak): peak to be analyzed

        Returns:
            Peak: peak with boundaries calculated

        Raises:
            ValueError: if peak index is not set
        """
        if peak.index is None:
            raise ValueError("Peak index is not set")
        left_base = peak.index
        while left_base > 0 and y[left_base-1] < y[left_base]:
            left_base -= 1

        right_base = peak.index
        while right_base < len(y)-1 and y[right_base+1] < y[right_base]:
            right_base += 1

        peak.left_base_index = left_base
        peak.right_base_index = right_base
        peak.left_base_time = x[left_base]
        peak.right_base_time = x[right_base]
        return peak


    @staticmethod
    def _calculate_peak_width(
        x: np.ndarray,
        y: np.ndarray,
        peak: Peak
    ) -> Peak:
        """Calculates the width of a peak.

        Args:
            x (np.ndarray): time values of the chromatogram
            y (np.ndarray): intensity values of the chromatogram
            peak (Peak): peak to be analyzed

        Returns:
            Peak: peak with width calculated

        Raises:
            None
        """
        peak = PeakAnalyzer._find_peak_boundaries(x, y, peak)
        peak.width = x[peak.right_base_index] - x[peak.left_base_index]
        return peak


    @staticmethod
    def _calculate_peak_area(
        x: np.ndarray,
        y: np.ndarray,
        peak: Peak
    ) -> Peak:
        """Calculates the area of a peak.

        Args:
            x (np.ndarray): time values of the chromatogram
            y (np.ndarray): intensity values of the chromatogram
            peak (Peak): peak to be analyzed

        Returns:
            float: area of the peak

        Raises:
            None
        """
        peak.area = trapz(y[peak.left_base_index:peak.right_base_index+1], x[peak.left_base_index:peak.right_base_index+1])
        return peak


    @staticmethod
    def _calculate_peak_symmetry(
        y: np.ndarray,
        peak: Peak
    ) -> Peak:
        """Calculates the symmetry of a peak.

        Args:
            y (np.ndarray): intensity values of the chromatogram
            peak (Peak): peak to be analyzed

        Returns:
            Peak: peak with symmetry calculated

        Raises:
            None
        """
        left_half = y[peak.left_base:peak.index+1]
        right_half = y[peak.index:peak.right_base+1][::-1]

        min_length = min(len(left_half), len(right_half))
        left_half = left_half[-min_length:]
        right_half = right_half[-min_length:]

        peak.symmetry = 1 - np.mean(np.abs(left_half - right_half) / y[peak.index])
        return peak


    @staticmethod
    def _calculate_peak_skewness(
        y: np.ndarray,
        peak: Peak
    ) -> Peak:
        """Calculates the skewness of a peak.

        Args:
            y (np.ndarray): intensity values of the chromatogram
            peak (Peak): peak to be analyzed

        Returns:
            Peak: peak with skewness calculated

        Raises:
            None
        """
        _peak = y[peak.left_base:peak.right_base+1]
        _peak = (_peak - np.mean(_peak)) / np.std(_peak)
        peak.skewness = np.mean(_peak**3)
        return peak


    @staticmethod
    def _calculate_peak_score(
        peak: Peak
    ) -> Peak:
        """Calculates the score of a peak.

        Args:
            peak (Peak): peak to be analyzed

        Returns:
            Peak: peak with score calculated

        Raises:
            None
        """
        peak.score = peak.height * peak.area * peak.symmetry * peak.time / peak.width if peak.width > 0 else 0
        return peak
