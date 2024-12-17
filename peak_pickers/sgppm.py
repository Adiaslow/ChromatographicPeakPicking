# External imports
from dataclasses import dataclass, field
import logging
import numpy as np
from scipy.optimize import curve_fit
import sys
from typing import List, Union

# Internal imports
from analyzers.chromatogram_analyzer import ChromatogramAnalyzer
from baseline_correctors.swm import SWM
from configs.global_config import GlobalConfig
from configs.sgppm_config import SGPPMConfig
from core.chromatogram import Chromatogram
from peak_pickers.Ipeak_picker import IPeakPicker
from peak_pickers.peak_finder import PeakFinder
from utilities.gaussian_curve import gaussian_curve


@dataclass
class SGPPM(
    IPeakPicker[SGPPMConfig]
):
    """Class to implement the SGPPM peak picking algorithm.

    Attributes:
        config (SGPPMConfig): Configuration object for the SGPPM algorithm
        global_config (GlobalConfig): Global configuration object

    Methods:
        pick_peaks: Process chromatograms to identify and select peaks
        _fit_gaussians: Fit Gaussian curves to peaks in chromatogram
        _select_peak: Select the best peak based on height thresholds and Gaussian fit
    """
    config: SGPPMConfig = field(default_factory=SGPPMConfig)
    global_config: GlobalConfig = field(default_factory=GlobalConfig)


    def __post_init__(
        self
    ):
        """Initialize and configure logger for debug messages.

        Args:
            None

        Returns:
            None

        Raise:
            None
        """
        self.logger = logging.getLogger(__name__)

        if self.global_config.debug:
            # Create console handler with a higher log level
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)

            # Create formatter and add it to the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.DEBUG)

            # Prevent logger from propagating to root logger
            self.logger.propagate = False


    def pick_peaks(
        self,
        chromatograms: Union[List[Chromatogram],
            Chromatogram]
    ) -> Union[List[Chromatogram], Chromatogram]:
        """Process chromatograms to identify and select peaks.

        Args:
            chromatograms (Union[List[Chromatogram], Chromatogram]): Chromatogram(s) to process

        Returns:
            Union[List[Chromatogram], Chromatogram]: Processed chromatogram(s)

        Raises:
            ValueError: If chromatogram contains no signal data
        """
        if self.global_config.debug:
            self.logger.debug(f"Processing {'single chromatogram' if isinstance(chromatograms, Chromatogram) else f'{len(chromatograms)} chromatograms'}")

        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        analyzer = ChromatogramAnalyzer()
        swm = SWM()
        peak_finder = PeakFinder()

        for i, chrom in enumerate(chromatograms):
            if self.global_config.debug:
                if chrom.y is None or chrom.x is None:
                    raise ValueError("Chromatogram contains no signal data")
                self.logger.debug(f"Processing chromatogram {i+1}/{len(chromatograms)} (id={id(chrom)})")
                self.logger.debug(f"Initial data shape: ({len(chrom.x)}, {len(chrom.y)})")

            chrom = analyzer(chrom)
            if self.global_config.debug:
                self.logger.debug("Completed chromatogram analysis")

            chrom = swm(chrom)
            if self.global_config.debug:
                self.logger.debug("Completed baseline correction")

            chrom = peak_finder(chrom)
            if self.global_config.debug:
                self.logger.debug(f"Found {len(chrom.peaks)} initial peaks")

            chrom = self._fit_gaussians(chrom)
            if self.global_config.debug:
                self.logger.debug("Completed Gaussian fitting")

            chrom = self._select_peak(chrom)
            if self.global_config.debug:
                self.logger.debug(f"Selected {len(chrom.peaks)} final peaks")

        return chromatograms[0] if len(chromatograms) == 1 else chromatograms


    def _fit_gaussians(
        self,
        chrom: Chromatogram
    ) -> Chromatogram:
        """Fit Gaussian curves to peaks in chromatogram.

        Args:
            chrom (Chromatogram): Chromatogram with peaks

        Returns:
            Chromatogram with Gaussian fit parameters and errors

        Raises:
            None
        """
        if self.global_config.debug:
            self.logger.debug(f"Starting Gaussian fitting for {len(chrom.peaks)} peaks")

        peaks = chrom.peaks
        x = chrom.x
        y = chrom.y

        for i, peak in enumerate(peaks):
            if self.global_config.debug:
                self.logger.debug(f"Fitting peak {i+1}/{len(peaks)} at time {peak['time']:.2f}")

            peak_x = peak['time']
            peak_y = peak['height']

            try:
                # Fit the gaussian curve
                popt, pcov = curve_fit(gaussian_curve, x, y, p0=[peak_y, peak_x, 1])

                if self.global_config.debug:
                    self.logger.debug(f"Gaussian fit parameters - Height: {popt[0]:.2f}, Center: {popt[1]:.2f}, Width: {popt[2]:.2f}")

                # Store both the parameters and covariance matrix
                peak['gaussian_curve'] = popt
                peak['gaussian_covariance'] = pcov
                perr = np.sqrt(np.diag(pcov))
                peak['gaussian_std_errors'] = perr

                if self.global_config.debug:
                    self.logger.debug(f"Standard errors - Height: {perr[0]:.2f}, Center: {perr[1]:.2f}, Width: {perr[2]:.2f}")

            except Exception as e:
                if self.global_config.debug:
                    self.logger.error(f"Gaussian fitting failed for peak {i+1}: {str(e)}")

        chrom.peaks = peaks
        return chrom


    def _select_peak(
        self,
        chrom: Chromatogram
    ) -> Chromatogram:
        """Select the best peak based on height thresholds and Gaussian fit.

        Args:
            chrom (Chromatogram): Chromatogram with peaks

        Returns:
            Chromatogram with picked_peak set (if one is found)

        Raises:
            None
        """
        if self.global_config.debug:
            self.logger.debug(f"Starting peak selection from {len(chrom.peaks)} peaks")
            self.logger.debug(f"Height threshold: {self.config.height_threshold:.2f}")
            self.logger.debug(f"Relative height threshold: {self.config.pick_rel_height:.2f}")

        # Return early if no peaks
        if not chrom.peaks:
            if self.global_config.debug:
                self.logger.debug("No peaks found, returning chromatogram")
            return chrom

        # Get maximum signal intensity
        max_y = np.max(chrom.y)
        if self.global_config.debug:
            self.logger.debug(f"Maximum signal intensity: {max_y:.2f}")

        # Filter peaks based on thresholds
        valid_peaks = []
        for i, peak in enumerate(chrom.peaks):
            peak_height = peak['height']
            is_valid = (peak_height >= self.config.height_threshold and
                       peak_height >= max_y * self.config.pick_rel_height)

            if self.global_config.debug:
                self.logger.debug(f"Peak {i+1} - Height: {peak_height:.2f}, Valid: {is_valid}")

            if is_valid:
                valid_peaks.append(peak)

        # Return if no valid peaks found
        if not valid_peaks:
            if self.global_config.debug:
                self.logger.debug("No peaks meet threshold criteria")
            return chrom

        # Select peak with highest intensity
        best_peak = max(valid_peaks, key=lambda p: p['time'])
        if self.global_config.debug:
            self.logger.debug(f"Selected best peak - Height: {best_peak['height']:.2f}, Time: {best_peak['time']:.2f}")

        # Set the picked peak but keep all peaks
        chrom.picked_peak = best_peak

        return chrom
