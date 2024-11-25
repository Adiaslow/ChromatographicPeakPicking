from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
from scipy.signal import find_peaks, peak_widths, savgol_filter
from scipy.signal.windows import tukey
from scipy.interpolate import interp1d
from typing import List, Optional, Tuple, Union

from .baseline_corrector import BaselineCorrector
from .chromatogram import Chromatogram
from .chromatogram_analyzer import ChromatogramAnalyzer
from .gaussian_curve import gaussian_curve
from .peak import Peak
from .peak_analyzer import PeakAnalyzer
from .peak_picker import PeakPicker
from .sgppm_config import SGPPMConfig

import warnings
warnings.filterwarnings('ignore', category=OptimizeWarning)

@dataclass
class SimpleGaussianPeakPickingModel(PeakPicker[SGPPMConfig]):
    config: SGPPMConfig = SGPPMConfig()

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        chromatograms = self._prepare_chromatograms(chromatograms)

        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)

        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        return chromatograms[0] if len(chromatograms) == 1 else chromatograms

    def _prepare_chromatograms(self, chromatograms: List[Chromatogram], method=SGPPMConfig.correction_method) -> List[Chromatogram]:
        for chrom in chromatograms:
            chrom.y_corrected = BaselineCorrector.correct_baseline(
                y=chrom.y,
                method=self.config.correction_method
            )
        return chromatograms

    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        for chrom in chromatograms:
            search_peaks, properties = find_peaks(chrom.y_corrected,
                height=chrom.y.max() * self.config.search_rel_height,
                rel_height=self.config.search_rel_height)

            fitted_peaks = []
            for idx, peak_idx in enumerate(search_peaks):
                peak_obj = Peak()
                width_points = peak_widths(chrom.y_corrected, [peak_idx], rel_height=0.5)
                left_idx = int(width_points[2][0])
                right_idx = int(width_points[3][0])

                peak_obj.peak_metrics.update({
                    'index': peak_idx,
                    'time': chrom.x[peak_idx],
                    'height': chrom.y_corrected[peak_idx],
                    'left_base_index': left_idx,
                    'right_base_index': right_idx,
                    'left_base_time': chrom.x[left_idx],
                    'right_base_time': chrom.x[right_idx],
                    'width': chrom.x[right_idx] - chrom.x[left_idx]
                })

                peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)
                if peak_obj.peak_metrics.get('fit_stddev', float('inf')) < self.config.stddev_threshold:
                    fitted_peaks.append(peak_obj)
                peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)

            chrom.peaks = fitted_peaks
        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """
        Fit a Gaussian curve to peak data with interpolation for smoother results.

        Args:
            x: x-axis data
            y: y-axis data (baseline corrected)
            peak: Peak object containing initial peak metrics
        """
        left_idx = max(0, int(peak.peak_metrics['left_base_index']))
        right_idx = min(len(x) - 1, int(peak.peak_metrics['right_base_index']))

        section_x = x[left_idx:right_idx + 1]
        section_y = y[left_idx:right_idx + 1]

        if len(section_x) < 3:  # Need at least 3 points for fitting
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': 'Not enough points for fitting'
            })
            return peak

        try:
            # Create higher resolution x-values for interpolation
            interp_factor = 10
            x_interp = np.linspace(section_x[0], section_x[-1], len(section_x) * interp_factor)

            # Smooth the section data
            window_length = min(7, len(section_y) - (len(section_y) % 2 + 1))
            if window_length >= 3:
                section_y_smooth = savgol_filter(section_y, window_length, 2)
            else:
                section_y_smooth = section_y

            # Interpolate the smoothed data
            interp_func = interp1d(section_x, section_y_smooth, kind='cubic', bounds_error=False, fill_value=0)
            y_interp = interp_func(x_interp)

            # Get peak properties from interpolated data
            peak_idx = np.argmax(y_interp)
            height = np.max(y_interp)
            mean = x_interp[peak_idx]

            # Width estimation using interpolated data
            peak_mask = y_interp > (height * 0.1)
            peak_indices = np.where(peak_mask)[0]
            if len(peak_indices) >= 2:
                width = (x_interp[peak_indices[-1]] - x_interp[peak_indices[0]]) / 4
            else:
                width = (section_x[-1] - section_x[0]) / 6

            # Initial parameters with adjusted bounds
            p0 = [height, mean, width]
            bounds = (
                [height * 0.7, x_interp[0], width * 0.3],
                [height * 1.3, x_interp[-1], width * 2.0]
            )

            # Create weights for interpolated data
            weights = np.ones_like(x_interp)
            peak_region = (x_interp > mean - width * 2) & (x_interp < mean + width * 2)
            weights[peak_region] = 3.0
            weights[y_interp < height * 0.1] = 0.5

            # Fit using interpolated data
            popt, _ = curve_fit(
                gaussian_curve,
                x_interp,
                y_interp,
                p0=p0,
                bounds=bounds,
                sigma=1/weights,
                maxfev=5000,
                method='trf'
            )

            # Generate the full curve
            fitted_curve = np.zeros_like(x)

            # Calculate the high-resolution curve
            x_high_res = np.linspace(x[0], x[-1], len(x) * interp_factor)
            curve_high_res = gaussian_curve(x_high_res, *popt)

            # Apply damping at edges if needed
            if left_idx > 0:
                left_mask = x_high_res < x[left_idx]
                damping = np.exp(-(x[left_idx] - x_high_res[left_mask]) / width)
                curve_high_res[left_mask] *= damping

            if right_idx < len(x) - 1:
                right_mask = x_high_res > x[right_idx]
                damping = np.exp(-(x_high_res[right_mask] - x[right_idx]) / width)
                curve_high_res[right_mask] *= damping

            # Interpolate back to original grid
            interp_func = interp1d(x_high_res, curve_high_res, kind='cubic', bounds_error=False, fill_value=0)
            fitted_curve = interp_func(x)

            # Calculate residuals using original data points
            section_fit = gaussian_curve(section_x, *popt)
            residuals = np.sum((section_y - section_fit)**2)
            normalized_residuals = residuals / (height * len(section_y))

            peak.peak_metrics.update({
                'gaussian_residuals': normalized_residuals,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'approximation_curve': fitted_curve
            })

        except (RuntimeError, ValueError) as e:
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': str(e)
            })

        return peak

    def _generate_interpolated_curve(self, x, x_interp, popt, left_idx, right_idx):
        """Generate smooth curve using interpolation and proper decay to zero"""
        # Generate high-resolution curve for the entire x range
        x_full_interp = np.linspace(x[0], x[-1], len(x) * 10)
        curve_full = np.zeros_like(x_full_interp)

        # Find indices corresponding to the section boundaries in interpolated space
        left_interp = np.searchsorted(x_full_interp, x[left_idx])
        right_interp = np.searchsorted(x_full_interp, x[right_idx])

        # Generate the main fitted section with high resolution
        section_mask = slice(left_interp, right_interp)
        curve_full[section_mask] = gaussian_curve(x_full_interp[section_mask], *popt)

        # Apply smooth decay outside the fitting region
        if left_interp > 0:
            left_x = x_full_interp[:left_interp]
            left_y = gaussian_curve(left_x, *popt)
            damping = np.exp(-(np.arange(len(left_x))[::-1]) / (len(left_x) / 3))
            curve_full[:left_interp] = left_y * damping

        if right_interp < len(x_full_interp):
            right_x = x_full_interp[right_interp:]
            right_y = gaussian_curve(right_x, *popt)
            damping = np.exp(-np.arange(len(right_x)) / (len(right_x) / 3))
            curve_full[right_interp:] = right_y * damping

        # Interpolate back to original x grid
        interp_func = interp1d(x_full_interp, curve_full, kind='cubic', bounds_error=False, fill_value=0)
        return interp_func(x)

    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        for chrom in chromatograms:
            if not chrom.peaks:
                continue

            max_y = np.max(chrom.y_corrected)
            valid_peaks = []

            for peak in chrom.peaks:
                peak_height = peak.peak_metrics['height']
                if (peak_height >= self.config.height_threshold and
                    peak_height >= max_y * self.config.pick_rel_height):
                    valid_peaks.append(peak)

            if valid_peaks:
                best_peak = max(valid_peaks, key=lambda p: p.peak_metrics['time'])
                chrom.picked_peak = best_peak

        return chromatograms
