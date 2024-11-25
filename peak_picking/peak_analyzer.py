from dataclasses import dataclass
import numpy as np
from scipy.signal import peak_widths
from scipy.integrate import trapz

from .peak import Peak
from .chromatogram import Chromatogram

@dataclass
class PeakAnalyzer:
   """Analyzes individual peak characteristics"""

   @staticmethod
   def analyze_peak(peak: Peak, chromatogram: Chromatogram) -> Peak:
       x, y = chromatogram.x, chromatogram.y_corrected
       peak = PeakAnalyzer._calculate_peak_boundaries(x, y, peak)
       peak = PeakAnalyzer._calculate_peak_width(x, y, peak)
       peak = PeakAnalyzer._calculate_peak_area(x, y, peak)
       peak = PeakAnalyzer._calculate_peak_symmetry(y, peak)
       peak = PeakAnalyzer._calculate_peak_skewness(y, peak)
       peak = PeakAnalyzer._calculate_peak_resolution(x, y, peak)
       peak = PeakAnalyzer._calculate_peak_gaussian_fit(x, y, peak)
       peak = PeakAnalyzer._calculate_peak_score(peak)
       return peak

   @staticmethod
   def _calculate_peak_boundaries(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
       left = peak.index
       while left > 0 and y[left-1] < y[left]: left -= 1

       right = peak.index
       while right < len(y)-1 and y[right+1] < y[right]: right += 1

       peak.left_base_index, peak.right_base_index = left, right
       peak.left_base_time, peak.right_base_time = x[left], x[right]
       return peak

   @staticmethod
   def _calculate_peak_width(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
       widths = peak_widths(y, [peak.index])
       peak.width = widths[0][0]
       peak.width_5 = widths[0][0] * 2.355  # FWHM to width at 5%
       return peak

   @staticmethod
   def _calculate_peak_area(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
       peak.area = trapz(y[peak.left_base_index:peak.right_base_index+1],
                        x[peak.left_base_index:peak.right_base_index+1])
       return peak

   @staticmethod
   def _calculate_peak_symmetry(y: np.ndarray, peak: Peak) -> Peak:
       left = y[peak.left_base_index:peak.index+1]
       right = y[peak.index:peak.right_base_index+1][::-1]
       min_len = min(len(left), len(right))
       peak.symmetry = 1 - np.mean(np.abs(left[-min_len:] - right[-min_len:]) / y[peak.index])
       return peak

   @staticmethod
   def _calculate_peak_skewness(y: np.ndarray, peak: Peak) -> Peak:
       peak_y = y[peak.left_base_index:peak.right_base_index+1]
       peak_y = (peak_y - np.mean(peak_y)) / np.std(peak_y)
       peak.skewness = np.mean(peak_y**3)
       return peak

   @staticmethod
   def _calculate_peak_resolution(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
       peaks, _ = find_peaks(y)
       if len(peaks) < 2:
           peak.resolution = float('inf')
           return peak

       distances = np.abs(peaks - peak.index)
       nearest = peaks[np.argsort(distances)[1]]  # First is self
       delta_t = abs(x[peak.index] - x[nearest])
       peak.resolution = 2 * delta_t / (peak.width + peak_widths(y, [nearest])[0][0])
       return peak

   @staticmethod
   def _calculate_peak_gaussian_fit(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
       section_x = x[peak.left_base_index:peak.right_base_index+1]
       section_y = y[peak.left_base_index:peak.right_base_index+1]
       try:
           popt, _ = curve_fit(gaussian_curve, section_x, section_y)
           peak.gaussian_residuals = np.sum((section_y - gaussian_curve(section_x, *popt))**2)
       except RuntimeError:
           peak.gaussian_residuals = float('inf')
       return peak

   @staticmethod
   def _calculate_peak_score(peak: Peak) -> Peak:
       metrics = [
           peak.symmetry,
           1 / (1 + peak.gaussian_residuals),
           min(peak.resolution / 2, 1),
           1 - abs(peak.skewness) / 2
       ]
       peak.score = np.mean(metrics) * peak.height * peak.area / peak.width
       return peak
