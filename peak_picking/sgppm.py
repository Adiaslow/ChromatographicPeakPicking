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
        Fit a Gaussian curve to baseline-corrected peak data.

        Args:
            x: x-axis data
            y: y-axis data (already baseline corrected)
            peak: Peak object containing initial peak metrics

        Returns:
            Peak object with updated metrics and fitted curve
        """
        # Get fitting region
        left_idx = int(peak.peak_metrics['left_base_index'])
        right_idx = int(peak.peak_metrics['right_base_index'])

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            # Initial parameter estimation
            height = peak.peak_metrics['height']
            peak_idx = peak.peak_metrics['index']
            mean = x[peak_idx]

            # Improved width estimation using peak shape analysis
            half_height = height / 2
            peak_relative_idx = peak_idx - left_idx

            # Find width using interpolation on both sides of peak
            try:
                left_half = np.interp(half_height,
                                    section_y[:peak_relative_idx][::-1],
                                    section_x[:peak_relative_idx][::-1])
                right_half = np.interp(half_height,
                                     section_y[peak_relative_idx:],
                                     section_x[peak_relative_idx:])
                width = (right_half - left_half) / 2.355  # Convert FWHM to sigma
            except ValueError:
                # Fallback width estimation if interpolation fails
                width = (x[right_idx] - x[left_idx]) / 4

            # Initial parameters and bounds
            p0 = [height, mean, width]
            bounds = (
                [height * 0.5, x[left_idx], width * 0.2],
                [height * 1.5, x[right_idx], width * 3.0]
            )

            # Weight the fit to emphasize the peak region
            weights = np.ones_like(section_x)
            peak_region = (section_x > mean - width) & (section_x < mean + width)
            weights[peak_region] = 2.0

            popt, pcov = curve_fit(
                gaussian_curve,
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
        """Generate smooth approximation curve with gradual decay to zero at boundaries"""
        curve = np.zeros_like(x)

        # Generate fitted values for section
        section_values = self.gaussian_curve(section_x, *popt)

        # Apply Gaussian tails naturally beyond the fitting region
        # This ensures smooth decay to zero
        curve[left_idx:right_idx] = section_values

        # Extend the Gaussian curve to the left if possible
        if left_idx > 0:
            left_x = x[:left_idx]
            curve[:left_idx] = self.gaussian_curve(left_x, *popt)

        # Extend the Gaussian curve to the right if possible
        if right_idx < len(x):
            right_x = x[right_idx:]
            curve[right_idx:] = self.gaussian_curve(right_x, *popt)

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
