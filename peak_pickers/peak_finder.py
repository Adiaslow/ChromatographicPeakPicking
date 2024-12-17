from dataclasses import dataclass, field
from typing import List
import numpy as np
from scipy.signal import find_peaks as sp_find_peaks
import logging
import sys

from analyzers.peak_analyzer import PeakAnalyzer
from configs.global_config import GlobalConfig
from configs.peak_finder_config import PeakFinderConfig
from core.chromatogram import Chromatogram
from core.peak import Peak

@dataclass
class PeakFinder:
    """Find peaks in chromatogram data using signal metrics for adaptive thresholds."""
    config: PeakFinderConfig = field(default_factory=PeakFinderConfig)
    global_config: GlobalConfig = field(default_factory=GlobalConfig)

    def __post_init__(self):
        """Initialize and configure logger for debug messages."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            # Set base logging level based on global config
            base_level = logging.DEBUG if self.global_config.debug else logging.INFO
            console_handler.setLevel(base_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(base_level)
            self.logger.propagate = False

    def _log_debug(self, message: str):
        """Helper method to only log debug messages if debug is enabled."""
        if self.global_config.debug:
            self.logger.debug(message)

    def find_peaks(self, chrom: Chromatogram) -> Chromatogram:
        """Find peaks in chromatogram using adaptive thresholds based on signal metrics."""
        self._log_debug(f"Starting peak finding for chromatogram {id(chrom)}")
        self._log_debug(f"Signal range: {np.min(chrom.y):.2f} to {np.max(chrom.y):.2f}")

        # Calculate adaptive thresholds from metrics
        height_threshold = self._calculate_height_threshold(chrom)
        prominence_threshold = self._calculate_prominence_threshold(chrom)
        width_threshold = self._calculate_width_threshold(chrom) * 0.01
        distance_threshold = 1
        window_length = self._calculate_window_length(chrom)

        self._log_debug("Calculated thresholds:")
        self._log_debug(f"  Height: {height_threshold:.2f}")
        self._log_debug(f"  Prominence: {prominence_threshold:.2f}")
        self._log_debug(f"  Width: {width_threshold:.2f}")
        self._log_debug(f"  Distance: {distance_threshold}")
        self._log_debug(f"  Window length: {window_length}")

        # Find peaks using scipy with adaptive parameters
        peak_indices, peak_properties = sp_find_peaks(
            chrom.y,
            height=height_threshold,
            prominence=prominence_threshold,
            width=width_threshold,
            distance=distance_threshold,
            wlen=window_length,
            rel_height=self.config.relative_height
        )

        self._log_debug(f"Found {len(peak_indices)} potential peaks")
        if len(peak_indices) > 0:
            if chrom.y is None:
                raise ValueError("Chromatogram must have signal data to find peaks.")
            self._log_debug("Peak heights found: " +
                        ", ".join([f"{chrom.y[idx]:.2f}" for idx in peak_indices]))

        peaks = self._create_peaks(chrom, peak_indices, peak_properties)
        self._log_debug(f"Created {len(peaks)} peak objects")

        chrom.add_peaks(peaks)
        return chrom

    def _calculate_height_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive height threshold."""
        snr_factor = max(
            self.config.min_snr_factor,
            min(chrom['signal_to_noise'] * self.config.snr_scale,
                self.config.max_snr_factor)
        )
        threshold = chrom['baseline_mean'] + (chrom['noise_level'] * snr_factor)
        self._log_debug("Height threshold calculation:")
        self._log_debug(f"  Baseline mean: {chrom['baseline_mean']:.2f}")
        self._log_debug(f"  Noise level: {chrom['noise_level']:.2f}")
        self._log_debug(f"  SNR factor: {snr_factor:.2f}")
        return threshold

    def _calculate_prominence_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive prominence threshold."""
        noise_based = chrom['noise_level'] * self.config.noise_prominence_factor
        range_based = chrom['dynamic_range'] * self.config.min_prominence_ratio
        threshold = max(noise_based, range_based)

        self._log_debug("Prominence threshold calculation:")
        self._log_debug(f"  Noise-based: {noise_based:.2f}")
        self._log_debug(f"  Range-based: {range_based:.2f}")
        return threshold

    def _calculate_width_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive width threshold."""
        if chrom.x is None:
            raise ValueError("Chromatogram must have time values to calculate width threshold.")
        sampling_rate = (chrom.x[-1] - chrom.x[0]) / len(chrom.x)
        roughness_factor = max(
            self.config.min_roughness_factor,
            min(chrom['baseline_roughness'] * self.config.roughness_scale,
                self.config.max_roughness_factor)
        )
        threshold = roughness_factor * sampling_rate

        self._log_debug("Width threshold calculation:")
        self._log_debug(f"  Sampling rate: {sampling_rate:.2f}")
        self._log_debug(f"  Roughness factor: {roughness_factor:.2f}")
        return threshold

    def _calculate_distance_threshold(self, chrom: Chromatogram) -> int:
        """Calculate minimum distance between peaks in data points."""
        width_threshold = self._calculate_width_threshold(chrom)
        return int(width_threshold * self.config.peak_separation_factor)

    def _calculate_window_length(self, chrom: Chromatogram) -> int:
        """Calculate window length for peak property calculations."""
        if chrom.x is None:
            raise ValueError("Chromatogram must have time values to calculate width threshold.")
        sampling_rate = (chrom.x[-1] - chrom.x[0]) / len(chrom.x)
        roughness_factor = max(
            self.config.min_window_roughness_factor,
            min(chrom['baseline_roughness'] * self.config.window_roughness_scale,
                self.config.max_window_roughness_factor)
        )
        return max(int(roughness_factor / sampling_rate),
                  self.config.min_window_points)

    def _create_peaks(self, chrom: Chromatogram, indices: np.ndarray, properties: dict) -> List[Peak]:
        """Create Peak objects from scipy.find_peaks results."""
        _peak_analyzer = PeakAnalyzer()
        peaks = []
        for i, idx in enumerate(indices):
            peak = Peak()

            if chrom.x is None:
                raise ValueError("Chromatogram must have time values to calculate width threshold.")
            peak['time'] = float(chrom.x[idx])
            peak['index'] = int(idx)
            peak['height'] = float(properties['peak_heights'][i])
            peak['prominence'] = float(properties['prominences'][i])
            peak['width'] = float(properties['widths'][i])
            peak['width_5'] = float(properties['width_heights'][i])

            left_base = int(properties['left_bases'][i])
            right_base = int(properties['right_bases'][i])
            peak['left_base_index'] = left_base
            peak['right_base_index'] = right_base
            peak['left_base_time'] = float(chrom.x[left_base])
            peak['right_base_time'] = float(chrom.x[right_base])

            peak = _peak_analyzer.analyze_peak(peak, chrom)
            peaks.append(peak)

            self._log_debug(f"Created peak at time {peak['time']:.2f}:")
            self._log_debug(f"  Height: {peak['height']:.2f}")
            self._log_debug(f"  Prominence: {peak['prominence']:.2f}")
            self._log_debug(f"  Width: {peak['width']:.2f}")

        return peaks

    def __call__(self, chrom: Chromatogram) -> Chromatogram:
        """Make the peak finder callable."""
        return self.find_peaks(chrom)
