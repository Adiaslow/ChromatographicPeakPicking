from dataclasses import dataclass
import numpy as np
from scipy.signal import peak_widths
from scipy.optimize import curve_fit
from typing import List

from core.chromatogram import Chromatogram
from core.peak import Peak

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
        peak = PeakAnalyzer._calculate_peak_prominence(y, peak)
        peak = PeakAnalyzer._calculate_gaussian_fit(x, y, peak)
        peak = PeakAnalyzer._calculate_peak_resolution(x, y, peak, chromatogram.peaks)
        peak = PeakAnalyzer._calculate_peak_score(peak)
        return peak

    @staticmethod
    def _gaussian(x: np.ndarray, amplitude: float, mean: float, std: float) -> np.ndarray:
        """Gaussian function for curve fitting."""
        return amplitude * np.exp(-(x - mean) ** 2 / (2 * std ** 2))

    @staticmethod
    def _calculate_peak_boundaries(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """Calculate peak boundaries by finding the valleys (local minima) on each side of the peak."""
        # Start from peak and move outward
        left = peak['index']
        right = peak['index']

        # Move left until we find a local minimum
        while left > 0 and not (y[left] <= y[left - 1] and y[left] <= y[left + 1]):
            left -= 1

        # Move right until we find a local minimum
        while right < len(y) - 1 and not (y[right] <= y[right - 1] and y[right] <= y[right + 1]):
            right += 1

        # Store boundaries
        peak['left_base_index'], peak['right_base_index'] = left, right
        peak['left_base_time'], peak['right_base_time'] = x[left], x[right]
        return peak

    @staticmethod
    def _calculate_gaussian_fit(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """Calculate how well the peak fits to a Gaussian shape.
        Implements more robust parameter estimation and fitting constraints.
        """
        # Get the peak region
        peak_slice = slice(peak['left_base_index'], peak['right_base_index'] + 1)
        x_peak = x[peak_slice]
        y_peak = y[peak_slice]

        # Background correction - subtract minimum in region
        y_baseline = min(y[peak['left_base_index']], y[peak['right_base_index']])
        y_peak_corrected = y_peak - y_baseline

        try:
            # More careful parameter estimation
            amplitude = peak['height'] - y_baseline
            mean = peak['time']
            # Estimate std from the width at half maximum
            half_max = amplitude / 2
            half_max_indices = np.where(y_peak_corrected >= half_max)[0]
            if len(half_max_indices) >= 2:
                sigma_estimate = (x_peak[half_max_indices[-1]] - x_peak[half_max_indices[0]]) / 2.355
            else:
                sigma_estimate = (x_peak[-1] - x_peak[0]) / 4  # fallback estimate

            # Initial guesses
            p0 = [amplitude, mean, max(sigma_estimate, 0.1)]

            # Reasonable bounds based on the data
            bounds = (
                [amplitude * 0.5, x_peak[0], sigma_estimate * 0.2],  # lower bounds
                [amplitude * 1.5, x_peak[-1], sigma_estimate * 5.0]  # upper bounds
            )

            # Fit with better constrained parameters
            popt, _ = curve_fit(PeakAnalyzer._gaussian, x_peak, y_peak_corrected,
                              p0=p0, bounds=bounds, maxfev=2000)

            # Calculate fitted values
            y_fit = PeakAnalyzer._gaussian(x_peak, *popt) + y_baseline

            # Calculate residuals as RMSE normalized by peak height
            residuals = np.sqrt(np.mean((y_peak - y_fit) ** 2)) / peak['height']
            peak['gaussian_residuals'] = residuals

            # Store fit parameters for debugging
            peak['gaussian_fit_params'] = {
                'amplitude': popt[0],
                'mean': popt[1],
                'sigma': popt[2],
                'baseline': y_baseline
            }

        except (RuntimeError, ValueError) as e:
            # If curve fitting fails, set a high residual value
            peak['gaussian_residuals'] = 1.0
            peak['gaussian_fit_params'] = {
                'error': str(e)
            }

        return peak

    @staticmethod
    def _calculate_peak_width(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        widths = peak_widths(y, [peak['index']])
        peak['width'] = widths[0][0]
        peak['width_5'] = widths[0][0] * 2.355
        return peak

    @staticmethod
    def _calculate_peak_area(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak['area'] = np.trapz(
            y[peak['left_base_index']:peak['right_base_index']+1],
            x[peak['left_base_index']:peak['right_base_index']+1]
        )
        return peak

    @staticmethod
    def _calculate_peak_symmetry(y: np.ndarray, peak: Peak) -> Peak:
        left = y[peak['left_base_index']:peak['index']+1]
        right = y[peak['index']:peak['right_base_index']+1][::-1]
        min_len = min(len(left), len(right))
        peak['symmetry'] = 1 - np.mean(np.abs(left[-min_len:] - right[-min_len:]) / y[peak['index']])
        return peak

    @staticmethod
    def _calculate_peak_skewness(y: np.ndarray, peak: Peak) -> Peak:
        peak_y = y[peak['left_base_index']:peak['right_base_index']+1]
        peak_y = (peak_y - np.mean(peak_y)) / np.std(peak_y)
        peak['skewness'] = np.mean(peak_y**3)
        return peak

    @staticmethod
    def _calculate_peak_resolution(x: np.ndarray, y: np.ndarray, peak: Peak, peaks: List[Peak]) -> Peak:
        all_peak_indices = [p['index'] for p in peaks]
        if len(all_peak_indices) < 2:
            peak['resolution'] = float('inf')
            return peak

        distances = np.abs(np.array(all_peak_indices) - peak['index'])
        nearest = all_peak_indices[np.argsort(distances)[1]]  # First is self
        delta_t = abs(x[peak['index']] - x[nearest])
        peak['resolution'] = 2 * delta_t / (peak['width'] + peak_widths(y, [nearest])[0][0])
        return peak

    @staticmethod
    def _calculate_peak_prominence(y: np.ndarray, peak: Peak) -> Peak:
        peak['prominence'] = peak['height'] - np.min([y[peak['left_base_index']], y[peak['right_base_index']]])
        return peak

    @staticmethod
    def _calculate_peak_score(peak: Peak) -> Peak:
        metrics = [
            peak['symmetry'],
            1 / (1 + peak['gaussian_residuals']),
            min(peak['resolution'] / 2, 1),
            1 - abs(peak['skewness']) / 2
        ]

        # Add time penalty directly in score calculation
        relative_time = peak['time'] / 60  # Assuming time is in minutes
        time_weight = (relative_time / 0.3) ** 6 if relative_time < 0.3 else 1.0

        peak['score'] = (np.mean(metrics) *
                        peak['prominence'] *
                        peak['area'] *
                        time_weight)
        return peak
