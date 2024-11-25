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
                                                height=self.config.height_threshold,
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

            chrom.peaks = fitted_peaks
        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak_idx = peak.peak_metrics['index']
        window = int(len(x) * 0.02)
        left_idx = max(0, peak_idx - window)
        right_idx = min(len(x), peak_idx + window)

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            height = peak.peak_metrics['height']
            mean = x[peak_idx]
            width = (section_x[-1] - section_x[0]) / 5.0

            amplitude_bounds = (height * 0.1, height * 2.0)
            mean_bounds = (section_x[0], section_x[-1])
            width_bounds = (width * 0.1, width * 5.0)

            p0 = [height, mean, width]
            bounds = ([amplitude_bounds[0], mean_bounds[0], width_bounds[0]],
                     [amplitude_bounds[1], mean_bounds[1], width_bounds[1]])

            popt, _ = curve_fit(gaussian_curve,
                              section_x,
                              section_y,
                              p0=p0,
                              bounds=bounds,
                              maxfev=2000)

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

            pick_peaks = []
            for peak in chrom.peaks:
                # Using pick_rel_height for final selection
                if peak.peak_metrics['height'] > (max(chrom.y_corrected) * self.config.pick_rel_height):
                    pick_peaks.append(peak)

            if pick_peaks:
                # Select peak with highest fitted amplitude
                best_peak = max(pick_peaks, key=lambda p: p.peak_metrics.get('fit_amplitude', 0))
                chrom.picked_peak = best_peak

        return chromatograms
