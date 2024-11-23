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
from peak_picking import chromatogram

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
        """Pick peaks in chromatograms.

        Args:
            chromatograms (Union[List[chrom], chrom]): chromatograms to be analyzed

        Returns:
            List[chrom]: chromatograms with peaks found and selected

        Raises:
            ValueError: if input is not a Chromatogram or a list of Chromatograms

        """
        if isinstance(chromatograms, Chromatogram):
                chromatograms = [chromatograms]
        elif not isinstance(chromatograms, list) or not all(isinstance(c, Chromatogram) for c in chromatograms):
            raise ValueError("Input must be a Chromatogram or a list of Chromatograms")


        chromatograms = self._prepare_chromatograms(chromatograms)
        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        if len(chromatograms) == 1:
            return chromatograms[0]
        return chromatograms


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
        """Find peaks in chromatograms

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found

        Raises:
            RuntimeError: if peak fitting fails
        """
        for chrom in chromatograms:
            peaks, properties = find_peaks(chrom.y_corrected, height=self.config.height_threshold)
            fitting_gaussians = []

            # Calculate peak widths
            widths = peak_widths(chrom.y_corrected, peaks, rel_height=self.config.search_rel_height)[0]

            # Process each peak
            for idx, peak in enumerate(peaks):
                # Check if peak is within valid range
                if chrom.x[peak] < min(chrom.x) or chrom.x[peak] > max(chrom.x):
                    continue

                # Calculate fitting window
                fit_width = widths[idx] + 1
                fit_x = np.linspace(chrom.x[peak] - fit_width, chrom.x[peak] + fit_width, self.config.fit_points)
                fit_y = np.interp(fit_x, chrom.x, chrom.y_corrected)

                if len(fit_x) < 3:
                    continue

                # Set up gaussian fitting parameters
                initial_guesses = [
                    properties['peak_heights'][idx],
                    chrom.x[peak],
                    widths[idx]
                ]

                bounds = (
                    [0, chrom.x[peak] - fit_width, 1e-6],
                    [properties['peak_heights'][idx] * 1.5, chrom.x[peak] + fit_width, fit_width]
                )

                try:
                    # Fit gaussian to peak
                    popt, _ = curve_fit(
                        gaussian_curve,
                        fit_x,
                        fit_y,
                        p0=initial_guesses,
                        bounds=bounds,
                        maxfev=3000
                    )
                except RuntimeError:
                    print(f"Could not fit a Gaussian to the peak at x = {chrom.x[peak]}")
                    continue

                # Validate fitted peak
                if popt[2] < self.config.stddev_threshold and min(chrom.x) <= popt[1] <= max(chrom.x):
                    window = tukey(len(fit_x), alpha=0.75)
                    fit_y_values = gaussian_curve(fit_x, *popt) * window
                    fitting_gaussians.append((fit_x, fit_y_values, popt))

            # Create Peak objects
            chrom.peaks = []
            for i, peak in enumerate(peaks):
                if i >= len(fitting_gaussians):
                    continue

                _peak = Peak(
                    time=chrom.x[peak],
                    index=peak,
                    height=chrom.y_corrected[peak],
                    approximation_curve=fitting_gaussians[i]
                )
                _peak = PeakAnalyzer.analyze_peak(_peak, chrom)
                chrom.peaks.append(_peak)

        return chromatograms

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
            chrom.picked_peak = None
            gaussians = [peak.approximation_curve for peak in chrom.peaks]

            if not gaussians:
                continue

            # Find valid gaussians based on height thresholds
            max_y = np.max(chrom.y_corrected)
            valid_gaussians = [
                (gaussian[2][1], gaussian)
                for gaussian in gaussians
                if (chrom.y_corrected[int(np.round(gaussian[2][1]))] >= self.config.height_threshold and
                    chrom.y_corrected[int(np.round(gaussian[2][1]))] >= max_y * self.config.pick_rel_height)
            ]

            if not valid_gaussians:
                continue

            # Select the best peak based on position
            best_mean, best_gaussian = max(valid_gaussians, key=lambda x: x[0])
            picked_peak = Peak(
                time=best_mean,
                index=int(np.round(best_mean)),
                height=chrom.y_corrected[int(np.round(best_mean))],
                approximation_curve=best_gaussian
            )
            peak_analyzer = PeakAnalyzer()

            chrom.picked_peak = peak_analyzer.analyze_peak(picked_peak, chrom)

        return chromatograms
