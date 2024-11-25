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
    """Class for peak picking of chromatograms using simple Gaussian fitting.

    Attributes:
        None

    Methods:
        pick_peak: Picks a peak from a chrom
        _find_product_peaks: Finds product peaks in a chrom
        _find_best_peak: Finds the best peak from a list of Gaussian fits based on given criteria
        _gaussian: Gaussian function
    """
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
        """Prepare chromatograms for peak picking.

        Args:
            chromatograms (List[chrom]): chromatograms to be prepared

        Returns:
            List[chrom]: chromatograms prepared for peak picking

        Raises:
            None
        """
        for chrom in chromatograms:
            chrom.y_corrected = BaselineCorrector.correct_baseline(
                y=chrom.y,
                method=self.config.correction_method
            )
        return chromatograms


    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        for chrom in chromatograms:
            noise_threshold = chrom.signal_metrics['noise_level'] * self.config.noise_factor
            min_distance = max(1, int(len(chrom.y_corrected) * self.config.min_distance_factor))

            # Add minimum prominence to favor larger peaks
            peaks, properties = find_peaks(chrom.y_corrected,
                                       height=noise_threshold,
                                       distance=min_distance,
                                       prominence=(np.max(chrom.y_corrected) * 0.1))

            fitted_peaks = self._fit_gaussians(chrom, peaks, properties)
            chrom.peaks = fitted_peaks

        return chromatograms


    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak_idx = peak.peak_metrics['index']

        # Use fixed window size relative to total chromatogram length
        window = int(len(x) * 0.02)  # 2% of total points
        left_idx = max(0, peak_idx - window)
        right_idx = min(len(x), peak_idx + window)

        section_x = x[left_idx:right_idx]
        section_y = y[left_idx:right_idx]

        try:
            # Ensure initial guess is within bounds
            height = peak.peak_metrics['height']
            mean = x[peak_idx]
            width = (section_x[-1] - section_x[0]) / 5.0

            # Set bounds relative to initial guess
            amplitude_bounds = (height * 0.1, height * 2.0)
            mean_bounds = (section_x[0], section_x[-1])
            width_bounds = (width * 0.1, width * 5.0)

            p0 = [height, mean, width]
            bounds = ([amplitude_bounds[0], mean_bounds[0], width_bounds[0]],
                     [amplitude_bounds[1], mean_bounds[1], width_bounds[1]])

            # Verify initial parameters are within bounds
            if not all(b[0] <= p <= b[1] for p, b in zip(p0, zip(*bounds))):
                raise RuntimeError("Initial parameters outside bounds")

            popt, _ = curve_fit(gaussian_curve,
                              section_x,
                              section_y,
                              p0=p0,
                              bounds=bounds,
                              maxfev=2000)

            peak.peak_metrics['gaussian_residuals'] = np.sum((section_y - gaussian_curve(section_x, *popt))**2) / height
            peak.peak_metrics['fit_amplitude'] = popt[0]
            peak.peak_metrics['fit_mean'] = popt[1]
            peak.peak_metrics['fit_stddev'] = popt[2]

            peak.peak_metrics['approximation_curve'] = np.zeros_like(x)
            peak.peak_metrics['approximation_curve'][left_idx:right_idx] = gaussian_curve(section_x, *popt)

        except (RuntimeError, ValueError):
            peak.peak_metrics['gaussian_residuals'] = float('inf')

        return peak

    def _fit_gaussians(self, chrom: Chromatogram, peaks: np.ndarray, properties: dict) -> List[Peak]:
        fitting_gaussians = []

        for idx, peak in enumerate(peaks):
            try:
                peak_obj = Peak()
                peak_obj.peak_metrics['index'] = peak
                peak_obj.peak_metrics['time'] = chrom.x[peak]
                peak_obj.peak_metrics['height'] = chrom.y[peak]
                peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)
                peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)
                fitting_gaussians.append(peak_obj)
            except RuntimeError:
                continue

        return fitting_gaussians

    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        for chrom in chromatograms:
            if not chrom.peaks:
                continue

            total_time = chrom.x[-1]
            for peak in chrom.peaks:
                relative_time = peak.peak_metrics['time'] / total_time

                # Only penalize final ~20% of gradient where dimers are likely
                if relative_time > 0.8:
                    time_weight = np.exp(-(relative_time - 0.8) / 0.1)
                else:
                    time_weight = 1.0

                peak.peak_metrics['score'] *= time_weight

            best_peak = max(chrom.peaks, key=lambda p: p.peak_metrics['score'])
            if self._validate_peak_metrics(best_peak, chrom):
                chrom.picked_peak = best_peak

        return chromatograms

    def _validate_peak_metrics(self, peak: Peak, chromatogram: Chromatogram, debug: bool = True) -> bool:
        def debug_print(msg: str):
            if debug:
                print(f"Peak at {peak.peak_metrics['time']:.2f} min failed: {msg}")

        if peak.peak_metrics['score'] <= 0:
            debug_print(f"score ({peak.peak_metrics['score']}) <= 0")
            return False

        if peak.peak_metrics['height'] < chromatogram.signal_metrics['noise_level'] * self.config.noise_factor:
            debug_print(f"height ({peak.peak_metrics['height']}) < noise threshold ({chromatogram.signal_metrics['noise_level'] * self.config.noise_factor})")
            return False

        # Convert width from minutes to relative scale
        peak_width_relative = peak.peak_metrics['width'] / (chromatogram.x[-1] - chromatogram.x[0])
        if not (self.config.width_min <= peak_width_relative <= self.config.width_max):
            debug_print(f"relative width ({peak_width_relative:.3f}) outside range [{self.config.width_min}, {self.config.width_max}]")
            return False

        if peak.peak_metrics['gaussian_residuals'] > self.config.gaussian_residuals_threshold:
            debug_print(f"gaussian residuals ({peak.peak_metrics['gaussian_residuals']:.2f}) > threshold ({self.config.gaussian_residuals_threshold})")
            return False

        if peak.peak_metrics['symmetry'] < self.config.symmetry_threshold:
            debug_print(f"symmetry ({peak.peak_metrics['symmetry']:.2f}) < threshold ({self.config.symmetry_threshold})")
            return False

        return True
