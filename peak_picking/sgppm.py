from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths
from scipy.signal.windows import tukey
from scipy.interpolate import interp1d
from typing import List, Optional, Tuple, Union

from .baseline_corrector import BaselineCorrector
from .chromatogram import Chromatogram
from .gaussian_curve import gaussian_curve
from .peak import Peak
from .peak_analyzer import PeakAnalyzer
from .peak_picker import PeakPicker
from .sgppm_config import SGPPMConfig

@dataclass
class SimpleGaussianPeakPickingModel(PeakPicker[SGPPMConfig]):
    """Class for peak picking of chromatograms using simple Gaussian fitting.

    Attributes:
        None

    Methods:
        pick_peak: Picks a peak from a chromatogram
        _find_product_peaks: Finds product peaks in a chromatogram
        _find_best_peak: Finds the best peak from a list of Gaussian fits based on given criteria
        _gaussian: Gaussian function
    """
    config: SGPPMConfig = SGPPMConfig()

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        """Pick peaks in chromatograms.

        Args:
            chromatograms (Union[List[Chromatogram], Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found and selected

        Raises:
            ValueError: if input is not a Chromatogram or a list of Chromatograms

        """
        if chromatograms is not List[Chromatogram] and chromatograms is Chromatogram:
            chromatograms = [chromatograms]
        else:
            raise ValueError("Input must be a Chromatogram or a list of Chromatograms")

        chromatograms = SimpleGaussianPeakPickingModel._prepare_chromatograms(chromatograms)
        chromatograms = SimpleGaussianPeakPickingModel._find_peaks(chromatograms)
        chromatograms = SimpleGaussianPeakPickingModel._select_peaks(chromatograms)

        if len(chromatograms) == 1:
            return chromatograms[0]
        return chromatograms


    def _prepare_chromatograms(self, chromatograms: List[Chromatogram], method=SGPPMConfig.correction_method) -> List[Chromatogram]:
        """Prepare chromatograms for peak picking.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be prepared

        Returns:
            List[Chromatogram]: chromatograms prepared for peak picking

        Raises:
            None
        """
        for chromatogram in chromatograms:
            chromatogram.y_corrected = BaselineCorrector.correct_baseline(y=chromatogram.y, method=method)
        return chromatograms


    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        for chromatogram in chromatograms:
            peaks, properties = find_peaks(chromatogram.y_corrected, height=SGPPMConfig.height_threshold)
            fitting_gaussians = []

            widths = peak_widths(chromatogram.y_corrected, peaks, rel_height=SGPPMConfig.search_rel_height)[0]

            for idx, peak in enumerate(peaks):
                if x[peak] < min(x) or x[peak] > max(x):
                    continue

                fit_width = widths[idx] + 1
                fit_indices = (chromatogram.x >= (chromatogram.x[peak] - fit_width)) \
                & (chromatogram.x <= (chromatogram.x[peak] + fit_width))

                fit_x = np.linspace(chromatogram.x[peak] - fit_width, chromatogram.x[peak] + fit_width, self.config.fit_points)
                fit_y = np.interp(fit_x, chromatogram.x, chromatogram.y_corrected)

                if len(fit_x) < 3:
                    continue

                initial_guesses = [
                    properties['peak_heights'][idx],
                    chromatogram.x[peak],
                    widths[idx]
                ]

                amplitude_bounds = (0, properties['peak_heights'][idx] * 1.5)
                mean_bounds = (chromatogram.x[peak] - fit_width, chromatogram.x[peak] + fit_width)
                stddev_bounds = (1e-6, fit_width)

                bounds = (
                    [amplitude_bounds[0], mean_bounds[0], stddev_bounds[0]],
                    [amplitude_bounds[1], mean_bounds[1], stddev_bounds[1]]
                )

                try:
                    popt, _ = curve_fit(
                        gaussian_curve,
                        fit_x,
                        fit_y,
                        p0=initial_guesses,
                        bounds=bounds,
                        maxfev=3000
                    )
                except RuntimeError:
                    print(f"Could not fit a Gaussian to the peak at x = {chromatogram.x[peak]}")
                    continue

                if popt[2] < SGPPMConfig.stddev_threshold and min(chromatogram.x) <= popt[1] <= max(chromatogram.x):
                    window = tukey(len(fit_x), alpha=0.75)
                    fit_y_values = gaussian_curve(fit_x, *popt) * window
                    fitting_gaussians.append((fit_x, fit_y_values, popt))

            for peak, i in enumerate(peaks):
                _peak = Peak(
                    time=chromatogram.x[int(peak)],
                    index=int(peak),
                    height=chromatogram.y_corrected[int(peak)],
                    approximation_curve=fitting_gaussians[i]
                )

                _peak = PeakAnalyzer.analyze_peak(chromatogram.x, chromatogram.y_corrected, _peak)
                chromatogram.peaks.append(_peak)
        return chromatograms


    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        if SGPPMConfig.height_threshold < 0 or SGPPMConfig.pick_rel_height < 0:
            raise ValueError("Height thresholds must be non-negative")
        for chromatogram in chromatograms:
            gaussians = [peak.approximation_curve for peak in chromatogram.peaks]
            if len(gaussians) == 0:
                try:
                    ValueError("No peaks found in chromatogram")
                except ValueError as e:
                    print(f"Caught error: {e}")
                return chromatograms

            max_y = np.max(chromatogram.y_corrected)
            valid_gaussians = [
                (gaussian[2][1], gaussian)
                for gaussian in gaussians:
                if (chromatogram.y_corrected[int(gaussian[2][1])] >= SGPPMConfig.height_threshold and
                    chromatogram.y_corrected[int(gaussian[2][1])] >= max_y * SGPPMConfig.pick_rel_height)
            ]

            if not valid_gaussians:
                try:
                    ValueError("No peaks found in chromatogram")
                except ValueError as e:
                    print(f"Caught error: {e}")
                return chromatograms

            best_mean, best_gaussian = max(valid_gaussians, key=lambda x: x[0])
            picked_peak = Peak(
                time=chromatogram.x[int(best_mean)],
                index=int(best_mean),
                height=chromatogram.y_corrected[int(best_mean)],
                approximation_curve=best_gaussian
            )
            picked_peak = PeakAnalyzer.analyze_peak(chromatogram.x, chromatogram.y_corrected, picked_peak)
        return chromatograms
