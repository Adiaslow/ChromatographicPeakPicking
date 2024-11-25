from dataclasses import dataclass
import numpy as np
from scipy.signal import peak_widths
from scipy.integrate import trapz
from typing import List

from .chromatogram import Chromatogram
from .peak import Peak

@dataclass
class PeakAnalyzer:
    @staticmethod
    def analyze_peak(peak: Peak, chromatogram: Chromatogram) -> Peak:
        x, y = chromatogram.x, chromatogram.y_corrected
        peak = PeakAnalyzer._calculate_peak_boundaries(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_width(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_area(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_symmetry(y, peak)
        peak = PeakAnalyzer._calculate_peak_skewness(y, peak)
        peak = PeakAnalyzer._calculate_peak_resolution(x, y, peak, chromatogram.peaks)
        return peak

    @staticmethod
    def _calculate_peak_boundaries(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        left = peak.peak_metrics['index']
        while left > 0 and y[left-1] < y[left]:
            left -= 1
        right = peak.peak_metrics['index']
        while right < len(y)-1 and y[right+1] < y[right]:
            right += 1
        peak.peak_metrics['left_base_index'], peak.peak_metrics['right_base_index'] = left, right
        peak.peak_metrics['left_base_time'], peak.peak_metrics['right_base_time'] = x[left], x[right]
        return peak

    @staticmethod
    def _calculate_peak_width(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        widths = peak_widths(y, [peak.peak_metrics['index']])
        peak.peak_metrics['width'] = widths[0][0]
        peak.peak_metrics['width_5'] = widths[0][0] * 2.355
        return peak


    @staticmethod
    def _calculate_peak_area(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak.peak_metrics['area'] = trapz(
            y[peak.peak_metrics['left_base_index']:peak.peak_metrics['right_base_index']+1],
            x[peak.peak_metrics['left_base_index']:peak.peak_metrics['right_base_index']+1]
        )
        return peak


    @staticmethod
    def _calculate_peak_symmetry(y: np.ndarray, peak: Peak) -> Peak:
        left = y[peak.peak_metrics['left_base_index']:peak.peak_metrics['index']+1]
        right = y[peak.peak_metrics['index']:peak.peak_metrics['right_base_index']+1][::-1]
        min_len = min(len(left), len(right))
        peak.peak_metrics['symmetry'] = 1 - np.mean(np.abs(left[-min_len:] - right[-min_len:]) / y[peak.peak_metrics['index']])
        return peak

    @staticmethod
    def _calculate_peak_skewness(y: np.ndarray, peak: Peak) -> Peak:
        peak_y = y[peak.peak_metrics['left_base_index']:peak.peak_metrics['right_base_index']+1]
        peak_y = (peak_y - np.mean(peak_y)) / np.std(peak_y)
        peak.peak_metrics['skewness'] = np.mean(peak_y**3)
        return peak


    @staticmethod
    def _calculate_peak_resolution(x: np.ndarray, y: np.ndarray, peak: Peak, peaks: List[Peak]) -> Peak:
        all_peak_indices = [p.peak_metrics['index'] for p in peaks]
        if len(all_peak_indices) < 2:
            peak.peak_metrics['resolution'] = float('inf')
            return peak

        distances = np.abs(np.array(all_peak_indices) - peak.peak_metrics['index'])
        nearest = all_peak_indices[np.argsort(distances)[1]]  # First is self
        delta_t = abs(x[peak.peak_metrics['index']] - x[nearest])
        peak.peak_metrics['resolution'] = 2 * delta_t / (peak.peak_metrics['width'] + peak_widths(y, [nearest])[0][0])
        return peak


    @staticmethod
    def _calculate_peak_score(peak: Peak) -> Peak:
        metrics = [
            peak.peak_metrics['symmetry'],
            1 / (1 + peak.peak_metrics['gaussian_residuals']),
            min(peak.peak_metrics['resolution'] / 2, 1),
            1 - abs(peak.peak_metrics['skewness']) / 2
        ]
        peak.peak_metrics['score'] = (np.mean(metrics) * peak.peak_metrics['height'] *
                                    peak.peak_metrics['area'] / peak.peak_metrics['width'])
        return peak
