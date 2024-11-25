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
        Fit a Gaussian curve to peak data with improved noise handling and peak shape estimation.

        Args:
            x: x-axis data
            y: y-axis data (baseline corrected)
            peak: Peak object containing initial peak metrics
        """
        left_idx = max(0, int(peak.peak_metrics['left_base_index']) - 2)
        right_idx = min(len(x), int(peak.peak_metrics['right_base_index']) + 2)

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            # Smooth the section data to reduce noise impact
            window_length = min(7, len(section_y) - (len(section_y) % 2 + 1))
            if window_length >= 3:
                section_y_smooth = savgol_filter(section_y, window_length, 2)
            else:
                section_y_smooth = section_y

            # Get peak properties
            peak_idx = peak.peak_metrics['index'] - left_idx
            height = np.max(section_y_smooth)
            mean = section_x[peak_idx]

            # Improved width estimation focusing on peak shape
            peak_mask = section_y_smooth > (height * 0.1)
            peak_indices = np.where(peak_mask)[0]
            if len(peak_indices) >= 2:
                width = (section_x[peak_indices[-1]] - section_x[peak_indices[0]]) / 4
            else:
                width = (x[right_idx] - x[left_idx]) / 6

            # Initial parameters with adjusted bounds
            p0 = [height, mean, width]
            bounds = (
                [height * 0.7, section_x[0], width * 0.3],
                [height * 1.3, section_x[-1], width * 2.0]
            )

            # Create weights emphasizing the peak region and de-emphasizing noise
            weights = np.ones_like(section_y)
            peak_region = (section_x > mean - width * 2) & (section_x < mean + width * 2)
            weights[peak_region] = 3.0
            weights[section_y < height * 0.1] = 0.5

            # Perform the fit
            popt, _ = curve_fit(
                gaussian_curve,  # Using imported gaussian_curve
                section_x,
                section_y_smooth,
                p0=p0,
                bounds=bounds,
                sigma=1/weights,
                maxfev=5000,
                method='trf'
            )

            # Generate the full curve
            fitted_curve = self._generate_approximation_curve(x, section_x, popt, left_idx, right_idx)

            # Calculate residuals using original data
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

    def _generate_approximation_curve(self, x, section_x, popt, left_idx, right_idx):
        """Generate the complete fitted curve ensuring smooth decay to zero"""
        curve = np.zeros_like(x)

        # Generate the main fitted section
        curve[left_idx:right_idx] = gaussian_curve(section_x, *popt)

        # Smoothly extend to zero outside the fitting region
        if left_idx > 0:
            left_x = x[:left_idx]
            left_y = gaussian_curve(left_x, *popt)
            damping = np.exp(-(np.arange(len(left_x))[::-1]) / 3)
            curve[:left_idx] = left_y * damping

        if right_idx < len(x):
            right_x = x[right_idx:]
            right_y = gaussian_curve(right_x, *popt)
            damping = np.exp(-np.arange(len(right_x)) / 3)
            curve[right_idx:] = right_y * damping

        return curve

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
