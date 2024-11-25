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
            # Calculate minimum peak distance based on min_distance_factor
            # Reduced from original to allow closer peaks
            min_distance = int(len(chrom.x) * (self.config.min_distance_factor * 0.5))

            # More lenient noise-based threshold
            noise_level = np.std(chrom.y_corrected[:100])
            dynamic_height_threshold = max(
                self.config.height_threshold * 0.7,  # Reduced height threshold
                noise_level * (self.config.noise_factor * 0.7)  # Reduced noise factor
            )

            # Wider acceptable width range
            sampling_rate = (chrom.x[-1] - chrom.x[0]) / len(chrom.x)
            width_min_points = int((self.config.width_min * 0.7) / sampling_rate)  # Reduced minimum width
            width_max_points = int((self.config.width_max * 1.5) / sampling_rate)  # Increased maximum width

            # Find peaks with more lenient criteria
            search_peaks, properties = find_peaks(
                chrom.y_corrected,
                height=dynamic_height_threshold,
                distance=min_distance,
                width=(width_min_points, width_max_points),
                rel_height=self.config.search_rel_height * 0.8,  # More lenient relative height
                prominence=(dynamic_height_threshold * 0.3, None)  # More lenient prominence
            )

            fitted_peaks = []
            for idx, peak_idx in enumerate(search_peaks):
                if peak_idx < 3 or peak_idx > len(chrom.x) - 3:  # Skip extreme edges
                    continue

                peak_obj = Peak()
                width_points = peak_widths(chrom.y_corrected, [peak_idx], rel_height=0.5)
                left_idx = int(width_points[2][0])
                right_idx = int(width_points[3][0])

                # More lenient edge handling
                if left_idx < 0:
                    left_idx = 0
                if right_idx >= len(chrom.x):
                    right_idx = len(chrom.x) - 1

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

                # More lenient width criteria for fitting
                if (peak_obj.peak_metrics['width'] >= self.config.width_min * 0.7 and
                    peak_obj.peak_metrics['width'] <= self.config.width_max * 1.5):

                    peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)
                    # More lenient stddev threshold
                    if peak_obj.peak_metrics.get('fit_stddev', float('inf')) < self.config.stddev_threshold * 1.3:
                        fitted_peaks.append(peak_obj)
                        peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)

            chrom.peaks = fitted_peaks
        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        left_idx = int(peak.peak_metrics['left_base_index'])
        right_idx = int(peak.peak_metrics['right_base_index'])

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            height = peak.peak_metrics['height']
            peak_idx = peak.peak_metrics['index']
            mean = x[peak_idx]

            # Width estimate from peak boundaries
            width = (x[right_idx] - x[left_idx]) / 2.355

            # Adjusted bounds for better fitting
            amplitude_bounds = (height * 0.5, height * 2.0)
            mean_bounds = (x[left_idx], x[right_idx])
            width_bounds = (width * 0.3, width * 2.0)

            p0 = [height, mean, width]
            bounds = ([amplitude_bounds[0], mean_bounds[0], width_bounds[0]],
                     [amplitude_bounds[1], mean_bounds[1], width_bounds[1]])

            popt, _ = curve_fit(gaussian_curve,
                              section_x,
                              section_y,
                              p0=p0,
                              bounds=bounds,
                              maxfev=5000)

            peak.peak_metrics.update({
                'gaussian_residuals': np.sum((section_y - gaussian_curve(section_x, *popt))**2) / height,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'approximation_curve': self._generate_approximation_curve(x, section_x, popt, left_idx, right_idx)
            })

        except (RuntimeError, ValueError):
            peak.peak_metrics['gaussian_residuals'] = float('inf')

        return peak

    def _generate_approximation_curve(self, x, section_x, popt, left_idx, right_idx):
        curve = np.zeros_like(x)
        curve[left_idx:right_idx] = gaussian_curve(section_x, *popt)
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
