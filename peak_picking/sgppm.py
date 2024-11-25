from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
from scipy.signal import find_peaks, peak_widths
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
        Fit a Gaussian curve to peak data with improved boundary handling and baseline correction.

        Args:
            x: x-axis data
            y: y-axis data
            peak: Peak object containing initial peak metrics

        Returns:
            Peak object with updated metrics and fitted curve
        """
        # Extend fitting region slightly beyond base indices for better boundary behavior
        left_idx = max(0, int(peak.peak_metrics['left_base_index']) - 5)
        right_idx = min(len(x), int(peak.peak_metrics['right_base_index']) + 5)

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            # Initial parameter estimation
            height = peak.peak_metrics['height']
            peak_idx = peak.peak_metrics['index']
            mean = x[peak_idx]

            # Improved width estimation using peak shape analysis
            half_height = height / 2
            left_half = np.interp(half_height,
                                section_y[:peak_idx-left_idx][::-1],
                                section_x[:peak_idx-left_idx][::-1])
            right_half = np.interp(half_height,
                                    section_y[peak_idx-left_idx:],
                                    section_x[peak_idx-left_idx:])
            width = (right_half - left_half) / 2.355  # Convert FWHM to sigma

            # Estimate baseline offset using edge points
            offset = min(section_y[0], section_y[-1])

            # Initial parameters and bounds
            p0 = [height - offset, mean, width, offset]
            bounds = (
                [0, section_x[0], width * 0.2, min(section_y) - 0.1 * height],
                [height * 2, section_x[-1], width * 3, max(section_y[0], section_y[-1]) + 0.1 * height]
            )

            # Weighted fitting to emphasize peak region
            weights = np.ones_like(section_y)
            peak_region = (section_x > mean - width) & (section_x < mean + width)
            weights[peak_region] = 2.0

            popt, pcov = curve_fit(
                self.gaussian_curve,
                section_x,
                section_y,
                p0=p0,
                bounds=bounds,
                sigma=1/weights,
                maxfev=10000
            )

            # Generate full curve and calculate metrics
            fitted_curve = self._generate_approximation_curve(x, section_x, popt, left_idx, right_idx)
            residuals = np.sum((section_y - self.gaussian_curve(section_x, *popt))**2)
            normalized_residuals = residuals / (height * len(section_y))

            # Update peak metrics
            peak.peak_metrics.update({
                'gaussian_residuals': normalized_residuals,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'fit_offset': popt[3],
                'fit_r_squared': 1 - (residuals / np.sum((section_y - np.mean(section_y))**2)),
                'approximation_curve': fitted_curve
            })

        except (RuntimeError, ValueError) as e:
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': str(e)
            })

        return peak

    def _generate_approximation_curve(self, x, section_x, popt, left_idx, right_idx):
        """Generate smooth approximation curve with zero-padding outside fitting region"""
        curve = np.zeros_like(x)

        # Generate fitted values for section
        section_values = self.gaussian_curve(section_x, *popt)

        # Smooth transition to zero at boundaries
        transition_points = 5
        left_transition = np.linspace(0, section_values[0], transition_points)
        right_transition = np.linspace(section_values[-1], 0, transition_points)

        # Insert main fitted section
        curve[left_idx:right_idx] = section_values

        # Apply transitions if there's room
        if left_idx >= transition_points:
            curve[left_idx-transition_points:left_idx] = left_transition
        if right_idx + transition_points <= len(curve):
            curve[right_idx:right_idx+transition_points] = right_transition

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
