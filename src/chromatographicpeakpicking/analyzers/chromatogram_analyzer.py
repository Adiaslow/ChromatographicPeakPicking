from dataclasses import dataclass, field
import logging
import sys
import numpy as np
from scipy import stats
from scipy import signal
from typing import List, Tuple

from ..configurations import ChromatogramAnalyzerConfig
from ..configurations import GlobalConfig
from core.chromatogram import Chromatogram

@dataclass
class ChromatogramAnalyzer:
    """Analyzer for computing chromatogram signal metrics.

    Attributes:
        global_config (GlobalConfig): Global configuration object
        logger (logging.Logger): Logger object for the analyzer
    """
    config: ChromatogramAnalyzerConfig = field(default_factory=ChromatogramAnalyzerConfig)
    global_config: GlobalConfig = field(default_factory=GlobalConfig)

    def __post_init__(self):
            """Initialize and configure logger for debug messages."""
            self.logger = logging.getLogger(__name__)
            if self.global_config.debug:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                if not self.logger.handlers:
                    self.logger.addHandler(console_handler)
                self.logger.setLevel(logging.DEBUG)
                self.logger.propagate = False

    def analyze_chromatogram(self, chrom: Chromatogram) -> Chromatogram:
        """Compute signal metrics for a chromatogram."""
        if self.global_config.debug:
            self.logger.debug(f"Beginning chromatogram analysis for chromatogram {id(chrom)}")

        self._validate_chromatogram(chrom)

        try:
            self._calculate_noise_metrics(chrom)
            self._calculate_baseline_metrics(chrom)
            self._calculate_area_metrics(chrom)
            self._calculate_distribution_metrics(chrom)
            self._calculate_quality_metrics(chrom)

        except Exception as e:
            if self.global_config.debug:
                self.logger.debug(f"Analysis failed with error: {str(e)}")
            raise RuntimeError(f"Failed to calculate signal metrics: {str(e)}") from e

        if self.global_config.debug:
            self.logger.debug("Chromatogram analysis completed successfully")

        return chrom

    def _validate_chromatogram(self, chrom: Chromatogram) -> None:
        """Validate chromatogram data before analysis."""
        if self.global_config.debug:
            if chrom.y is None or chrom.x is None:
                raise ValueError("Chromatogram contains no signal data")
            self.logger.debug(f"Validating chromatogram: id={id(chrom)}, shape=({len(chrom.x)}, {len(chrom.y)})")

        if not isinstance(chrom, Chromatogram):
            raise TypeError("Input must be a Chromatogram object")
        if chrom.y is None or chrom.x is None:
            raise ValueError("Chromatogram contains no signal data")
        if not isinstance(chrom.y, np.ndarray) or not isinstance(chrom.x, np.ndarray):
            raise ValueError("Chromatogram signals must be numpy arrays")
        if len(chrom.y) == 0 or len(chrom.x) == 0:
            raise ValueError("Chromatogram signals are empty")
        if len(chrom.y) != len(chrom.x):
            raise ValueError("X and Y arrays must have same length")

        # Split the finite checks into boolean masks first
        x_is_finite: np.ndarray = np.isfinite(chrom.x)  # type: ignore
        y_is_finite: np.ndarray = np.isfinite(chrom.y)  # type: ignore

        if self.global_config.debug and (not x_is_finite.all() or not y_is_finite.all()):
            self.logger.debug(f"Non-finite values found - X: {np.sum(~x_is_finite)}, Y: {np.sum(~y_is_finite)}")

        # Check if all values are finite
        if not x_is_finite.all() or not y_is_finite.all():
            raise ValueError("Chromatogram signals contain NaN or infinite values")

    def _calculate_moving_std(self, y: np.ndarray) -> np.ndarray:
        """Calculate moving standard deviation using convolution for efficiency."""
        if self.global_config.debug:
            self.logger.debug(f"Calculating moving standard deviation with window width {self.config.window_width}")

        # Create padded array to handle edges
        pad_width = self.config.window_width // 2
        y_padded = np.pad(y, pad_width, mode='edge')

        # Calculate moving mean using convolution
        window = np.ones(self.config.window_width) / self.config.window_width
        moving_mean = signal.convolve(y_padded, window, mode='valid')

        # Calculate moving variance using convolution
        y_squared = y_padded ** 2
        moving_mean_squared = signal.convolve(y_squared, window, mode='valid')
        moving_var = moving_mean_squared - moving_mean ** 2

        # Handle numerical errors that could lead to small negative variances
        moving_var = np.maximum(moving_var, 0)

        return np.sqrt(moving_var)

    def _find_minimal_variation_regions(self, moving_std: np.ndarray) -> List[Tuple[int, int]]:
        """Identify contiguous regions of minimal signal variation."""
        if self.global_config.debug:
            self.logger.debug("Identifying minimal variation regions")

        # Calculate threshold based on minimum std dev
        min_std = np.min(moving_std)
        threshold = min_std * self.config.variation_threshold

        # Exclude edges if configured
        start_idx = int(len(moving_std) * self.config.edge_exclusion)
        end_idx = len(moving_std) - start_idx

        # Find regions below threshold
        below_threshold = moving_std[start_idx:end_idx] < threshold

        # Find contiguous regions
        regions = []
        current_start = None

        for i, is_quiet in enumerate(below_threshold, start=start_idx):
            if is_quiet and current_start is None:
                current_start = i
            elif not is_quiet and current_start is not None:
                if i - current_start >= self.config.min_region_width:
                    regions.append((current_start, i))
                current_start = None

        # Handle case where quiet region extends to end
        if current_start is not None and end_idx - current_start >= self.config.min_region_width:
            regions.append((current_start, end_idx))

        # Merge nearby regions
        merged_regions = []
        if regions:
            current_start, current_end = regions[0]
            for start, end in regions[1:]:
                if start - current_end <= self.config.max_region_gap:
                    current_end = end
                else:
                    merged_regions.append((current_start, current_end))
                    current_start, current_end = start, end
            merged_regions.append((current_start, current_end))

        if self.global_config.debug:
            self.logger.debug(f"Found {len(merged_regions)} minimal variation regions")

        return merged_regions

    def _calculate_noise_metrics(self, chrom: Chromatogram) -> None:
        """Calculate and store noise-related metrics using minimal variation regions."""
        if self.global_config.debug:
            self.logger.debug("Calculating noise metrics using minimal variation regions")

        if chrom.y is None:
            raise ValueError("Chromatogram contains no signal data")

        # Calculate moving standard deviation
        moving_std = self._calculate_moving_std(chrom.y)

        # Find minimal variation regions
        quiet_regions = self._find_minimal_variation_regions(moving_std)

        if len(quiet_regions) < self.config.min_regions_required:
            if self.global_config.debug:
                self.logger.warning(f"Found only {len(quiet_regions)} regions, minimum required is {self.config.min_regions_required}")
            noise_level = float(np.std(chrom.y))
        else:
            # Calculate noise level as specified percentile of moving std in quiet regions
            quiet_stds = []
            for start, end in quiet_regions:
                quiet_stds.extend(moving_std[start:end])
            noise_level = float(np.percentile(quiet_stds, self.config.noise_percentile))

            # Validate noise estimate quality
            noise_variance = np.var([np.std(chrom.y[start:end]) for start, end in quiet_regions])
            if noise_variance > self.config.max_noise_variance and self.global_config.debug:
                self.logger.warning(f"High variance in noise estimates: {noise_variance:.2e}")

        # Calculate signal range and SNR
        signal_range = float(np.max(chrom.y) - np.min(chrom.y))
        snr = float('inf') if noise_level == 0 else signal_range / noise_level

        if self.global_config.debug:
            self.logger.debug(f"Noise metrics - level: {noise_level:.2e}, SNR: {snr:.2f}")
            self.logger.debug(f"Number of quiet regions: {len(quiet_regions)}")

        # Store metrics in chromatogram
        chrom['noise_level'] = noise_level
        chrom['signal_to_noise'] = snr
        chrom['quiet_regions'] = quiet_regions

    def _calculate_baseline_metrics(self, chrom: Chromatogram) -> None:
        """Calculate and store baseline-related metrics."""
        if self.global_config.debug:
            self.logger.debug("Calculating baseline metrics")

        baseline_mean = float(np.percentile(chrom.y, 10))
        try:
            coefficients = np.polyfit(chrom.x, chrom.y, 1)
            drift = float(coefficients[0])
        except np.RankWarning:
            if self.global_config.debug:
                self.logger.debug("RankWarning encountered in baseline drift calculation")
            drift = float(np.nan)

        if self.global_config.debug:
            self.logger.debug(f"Baseline metrics - mean: {baseline_mean:.2f}, drift: {drift:.2e}")

        chrom['baseline_mean'] = baseline_mean
        chrom['baseline_drift'] = drift

    def _calculate_area_metrics(self, chrom: Chromatogram) -> None:
        """Calculate and store area-related metrics."""
        if self.global_config.debug:
            self.logger.debug("Calculating area metrics")

        zeros = np.zeros_like(chrom.y)
        positive_y = np.where(chrom.y > zeros, chrom.y, zeros)  # type: ignore
        negative_y = np.where(chrom.y < zeros, chrom.y, zeros)  # type: ignore

        total_area = float(np.trapz(chrom.y, chrom.x))  # type: ignore
        positive_area = float(np.trapz(positive_y, chrom.x))  # type: ignore
        negative_area = float(np.trapz(negative_y, chrom.x))  # type: ignore

        if self.global_config.debug:
            self.logger.debug(f"Area metrics - total: {total_area:.2f}, positive: {positive_area:.2f}, negative: {negative_area:.2f}")

        chrom['total_area'] = total_area
        chrom['positive_area'] = positive_area
        chrom['negative_area'] = negative_area

    def _calculate_distribution_metrics(self, chrom: Chromatogram) -> None:
        """Calculate and store intensity distribution metrics."""
        if self.global_config.debug:
            self.logger.debug("Calculating distribution metrics")

        skewness = float(stats.skew(chrom.y))
        kurtosis = float(stats.kurtosis(chrom.y))
        dynamic_range = float(np.max(chrom.y) - np.min(chrom.y))  # type: ignore

        if self.global_config.debug:
            self.logger.debug(f"Distribution metrics - skewness: {skewness:.2f}, kurtosis: {kurtosis:.2f}, range: {dynamic_range:.2f}")

        chrom['skewness'] = skewness
        chrom['kurtosis'] = kurtosis
        chrom['dynamic_range'] = dynamic_range

    def _calculate_quality_metrics(self, chrom: Chromatogram) -> None:
        """Calculate and store chromatographic quality metrics."""
        if self.global_config.debug:
            self.logger.debug("Calculating quality metrics")

        smoothness = float(np.mean(np.abs(np.diff(chrom.y))))
        roughness = float(np.std(np.diff(chrom.y)))

        if self.global_config.debug:
            self.logger.debug(f"Quality metrics - smoothness: {smoothness:.2e}, roughness: {roughness:.2e}")

        chrom['signal_smoothness'] = smoothness
        chrom['baseline_roughness'] = roughness

    def __call__(self, chrom: Chromatogram) -> Chromatogram:
        """Shortcut for analyzing a chromatogram."""
        return self.analyze_chromatogram(chrom)
