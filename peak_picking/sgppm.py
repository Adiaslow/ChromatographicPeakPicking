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
            noise_threshold = chrom.signal_metrics['noise_level'] * 2  # Reduced from 3
            min_distance = max(1, int(len(chrom.y_corrected) * 0.005))  # Reduced from 0.01
            peaks, properties = find_peaks(chrom.y_corrected,
                                       height=noise_threshold,
                                       distance=min_distance)

            fitted_peaks = self._fit_gaussians(chrom, peaks, properties)
            chrom.peaks = [peak for peak in fitted_peaks
                         if peak.peak_metrics['gaussian_residuals'] <= 10.0]  # Increased from 1.0

            if chrom.peaks:
                print(f"Peak heights: {[p.peak_metrics['height'] for p in chrom.peaks]}")
                print(f"Peak residuals: {[p.peak_metrics['gaussian_residuals'] for p in chrom.peaks]}")

        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        section_x = x[peak.peak_metrics['left_base_index']:peak.peak_metrics['right_base_index']+1]
        section_y = y[peak.peak_metrics['left_base_index']:peak.peak_metrics['right_base_index']+1]

        try:
            popt, _ = curve_fit(gaussian_curve, section_x, section_y,
                               p0=[peak.peak_metrics['height'],
                                   x[peak.peak_metrics['index']],
                                   peak.peak_metrics['width']])

            peak.peak_metrics['gaussian_residuals'] = np.sum((section_y - gaussian_curve(section_x, *popt))**2)
            peak.peak_metrics['approximation_curve'] = gaussian_curve(x, *popt)  # Use full x range
        except RuntimeError:
            peak.peak_metrics['gaussian_residuals'] = float('inf')

        return peak

    def _fit_gaussians(self, chrom: Chromatogram, peaks: np.ndarray, properties: dict) -> List[Peak]:
        fitting_gaussians = []

        for idx, peak in enumerate(peaks):
            try:
                peak_obj = Peak()
                peak_obj.peak_metrics['index'] = peak
                peak_obj.peak_metrics['time'] = chrom.x[peak]
                peak_obj.peak_metrics['height'] = chrom.y_corrected[peak]
                peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)
                peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)
                fitting_gaussians.append(peak_obj)
            except RuntimeError:
                continue

        return fitting_gaussians

    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Select peaks in chromatograms

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks selected

        Raises:
            ValueError: if height thresholds are negative
        """
        if self.config.height_threshold < 0 or self.config.pick_rel_height < 0:
            raise ValueError("Height thresholds must be non-negative")

        for chrom in chromatograms:
            if not chrom.peaks:
                continue

            best_peak = max(chrom.peaks, key=lambda p: p.peak_metrics['score'])
            if self._validate_peak_metrics(best_peak, chrom):
                chrom.picked_peak = best_peak

        return chromatograms

    def _validate_peak_metrics(self, peak: Peak, chromatogram: Chromatogram) -> bool:
       """Validate peak metrics before selection"""
       if peak.peak_metrics['score'] <= 0:
           return False

       if peak.peak_metrics['gaussian_residuals'] > self.config.gaussian_residuals_threshold:
           return False

       if peak.peak_metrics['height'] < chromatogram.signal_metrics['noise_level'] * self.config.noise_factor:
           return False

       if not (self.config.width_min <= peak.peak_metrics['width'] <= len(chromatogram.x) * self.config.width_max):
           return False

       if peak.peak_metrics['symmetry'] < self.config.symmetry_threshold:
           return False

       return True
