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

                peak_obj = self._fit_gaussian(chrom.x, chrom.y, peak_obj)
                if peak_obj.peak_metrics.get('fit_stddev', float('inf')) < self.config.stddev_threshold:
                    fitted_peaks.append(peak_obj)

            chrom.peaks = fitted_peaks
        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak_idx = peak.peak_metrics['index']
        width = peak.peak_metrics['width']
        fit_width = width + 1

        # Create fit region
        fit_indices = (x >= (x[peak_idx] - fit_width)) & (x <= (x[peak_idx] + fit_width))
        fit_x = np.linspace(x[peak_idx] - fit_width, x[peak_idx] + fit_width, self.config.fit_points)
        fit_y = np.interp(fit_x, x[fit_indices], y[fit_indices])

        try:
            height = peak.peak_metrics['height']
            mean = x[peak_idx]

            p0 = [height, mean, width]
            bounds = ([0, mean - fit_width, 1e-6],
                     [height * 1.5, mean + fit_width, fit_width])

            popt, _ = curve_fit(gaussian_curve,
                              fit_x,
                              fit_y,
                              p0=p0,
                              bounds=bounds,
                              maxfev=3000)

            window = tukey(len(fit_x), alpha=0.75)
            fit_y_values = gaussian_curve(fit_x, *popt) * window

            peak.peak_metrics.update({
                'gaussian_residuals': np.sum((fit_y - fit_y_values)**2) / height,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'approximation_curve': np.zeros_like(x)
            })

            # Interpolate fitted values back to original x grid
            peak.peak_metrics['approximation_curve'][fit_indices] = np.interp(x[fit_indices], fit_x, fit_y_values)

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
