# src/chromatographicpeakpicking/analyzers/chromatogram_analyzer.py
from dataclasses import dataclass, field
import logging
import sys
import numpy as np
from scipy import stats
from scipy import signal
from typing import List, Tuple
from src.chromatographicpeakpicking.core.protocols.configurable import Configurable
from src.chromatographicpeakpicking.core.types.config import BaseConfig, ConfigMetadata, ConfigValidation
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.types.config import GlobalConfig

@dataclass
class ChromatogramAnalyzerConfig(BaseConfig):
    # Configuration parameters
    window_width: int = 15
    window_overlap: float = 0.5
    min_window_points: int = 5
    variation_threshold: float = 1.5
    min_region_width: int = 5
    max_region_gap: int = 20
    noise_percentile: float = 50.0
    min_regions_required: int = 3
    max_noise_variance: float = 2.0
    edge_exclusion: float = 0.05
    baseline_percentile: float = 10.0
    drift_window: int = 100
    smoothing_window: int = 5
    outlier_threshold: float = 3.0

    def __init__(self):
        super().__init__(metadata=ConfigMetadata(
            name="ChromatogramAnalyzerConfig",
            version="1.0",
            description="Configuration for Chromatogram Analyzer",
            defaults={
                "window_width": 15,
                "window_overlap": 0.5,
                "min_window_points": 5,
                "variation_threshold": 1.5,
                "min_region_width": 5,
                "max_region_gap": 20,
                "noise_percentile": 50.0,
                "min_regions_required": 3,
                "max_noise_variance": 2.0,
                "edge_exclusion": 0.05,
                "baseline_percentile": 10.0,
                "drift_window": 100,
                "smoothing_window": 5,
                "outlier_threshold": 3.0
            },
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters=self.__dict__)

@dataclass
class ChromatogramAnalyzer(Configurable[ChromatogramAnalyzerConfig]):
    config: ChromatogramAnalyzerConfig = field(default_factory=ChromatogramAnalyzerConfig)
    global_config: GlobalConfig = field(default_factory=GlobalConfig)

    def __post_init__(self):
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

    def configure(self, config: ChromatogramAnalyzerConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def get_metadata(self) -> ConfigMetadata:
        return self.config.metadata

    def validate_config(self, config: ChromatogramAnalyzerConfig) -> ValidationResult:
        errors = []
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def analyze_chromatogram(self, chrom: Chromatogram) -> Chromatogram:
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
        if self.global_config.debug:
            if chrom.intensity is None or chrom.time is None:
                raise ValueError("Chromatogram contains no signal data")
            self.logger.debug(f"Validating chromatogram: id={id(chrom)}, shape=({len(chrom.time)}, {len(chrom.intensity)})")

        if not isinstance(chrom, Chromatogram):
            raise TypeError("Input must be a Chromatogram object")
        if chrom.intensity is None or chrom.time is None:
            raise ValueError("Chromatogram contains no signal data")
        if not isinstance(chrom.intensity, np.ndarray) or not isinstance(chrom.time, np.ndarray):
            raise ValueError("Chromatogram signals must be numpy arrays")
        if len(chrom.intensity) == 0 or len(chrom.time) == 0:
            raise ValueError("Chromatogram signals are empty")
        if len(chrom.intensity) != len(chrom.time):
            raise ValueError("Time and intensity arrays must have same length")

        time_is_finite: np.ndarray = np.isfinite(chrom.time)
        intensity_is_finite: np.ndarray = np.isfinite(chrom.intensity)

        if self.global_config.debug and (not time_is_finite.all() or not intensity_is_finite.all()):
            self.logger.debug(f"Non-finite values found - Time: {np.sum(~time_is_finite)}, Intensity: {np.sum(~intensity_is_finite)}")

        if not time_is_finite.all() or not intensity_is_finite.all():
            raise ValueError("Chromatogram signals contain NaN or infinite values")

    def _calculate_moving_std(self, intensity: np.ndarray) -> np.ndarray:
        if self.global_config.debug:
            self.logger.debug(f"Calculating moving standard deviation with window width {self.config.window_width}")

        pad_width = self.config.window_width // 2
        intensity_padded = np.pad(intensity, pad_width, mode='edge')

        window = np.ones(self.config.window_width) / self.config.window_width
        moving_mean = signal.convolve(intensity_padded, window, mode='valid')

        intensity_squared = intensity_padded ** 2
        moving_mean_squared = signal.convolve(intensity_squared, window, mode='valid')
        moving_var = moving_mean_squared - moving_mean ** 2

        moving_var = np.maximum(moving_var, 0)

        return np.sqrt(moving_var)

    def _find_minimal_variation_regions(self, moving_std: np.ndarray) -> List[Tuple[int, int]]:
        if self.global_config.debug:
            self.logger.debug("Identifying minimal variation regions")

        min_std = np.min(moving_std)
        threshold = min_std * self.config.variation_threshold

        start_idx = int(len(moving_std) * self.config.edge_exclusion)
        end_idx = len(moving_std) - start_idx

        below_threshold = moving_std[start_idx:end_idx] < threshold

        regions = []
        current_start = None

        for i, is_quiet in enumerate(below_threshold, start=start_idx):
            if is_quiet and current_start is None:
                current_start = i
            elif not is_quiet and current_start is not None:
                if i - current_start >= self.config.min_region_width:
                    regions.append((current_start, i))
                current_start = None

        if current_start is not None and end_idx - current_start >= self.config.min_region_width:
            regions.append((current_start, end_idx))

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
        if self.global_config.debug:
            self.logger.debug("Calculating noise metrics using minimal variation regions")

        if chrom.intensity is None:
            raise ValueError("Chromatogram contains no signal data")

        moving_std = self._calculate_moving_std(chrom.intensity)

        quiet_regions = self._find_minimal_variation_regions(moving_std)

        if len(quiet_regions) < self.config.min_regions_required:
            if self.global_config.debug:
                self.logger.warning(f"Found only {len(quiet_regions)} regions, minimum required is {self.config.min_regions_required}")
            noise_level = float(np.std(chrom.intensity))
        else:
            quiet_stds = []
            for start, end in quiet_regions:
                quiet_stds.extend(moving_std[start:end])
            noise_level = float(np.percentile(quiet_stds, self.config.noise_percentile))

            noise_variance = np.var([np.std(chrom.intensity[start:end]) for start, end in quiet_regions])
            if noise_variance > self.config.max_noise_variance and self.global_config.debug:
                self.logger.warning(f"High variance in noise estimates: {noise_variance:.2e}")

        signal_range = float(np.max(chrom.intensity) - np.min(chrom.intensity))
        snr = float('inf') if noise_level == 0 else signal_range / noise_level

        if self.global_config.debug:
            self.logger.debug(f"Noise metrics - level: {noise_level:.2e}, SNR: {snr:.2f}")
            self.logger.debug(f"Number of quiet regions: {len(quiet_regions)}")

        chrom.metadata['noise_level'] = noise_level
        chrom.metadata['signal_to_noise'] = snr
        chrom.metadata['quiet_regions'] = quiet_regions

    def _calculate_baseline_metrics(self, chrom: Chromatogram) -> None:
        if self.global_config.debug:
            self.logger.debug("Calculating baseline metrics")

        baseline_mean = float(np.percentile(chrom.intensity, self.config.baseline_percentile))
        try:
            coefficients = np.polyfit(chrom.time, chrom.intensity, 1)
            drift = float(coefficients[0])
        except np.RankWarning:
            if self.global_config.debug:
                self.logger.debug("RankWarning encountered in baseline drift calculation")
            drift = float(np.nan)

        if self.global_config.debug:
            self.logger.debug(f"Baseline metrics - mean: {baseline_mean:.2f}, drift: {drift:.2e}")

        chrom.metadata['baseline_mean'] = baseline_mean
        chrom.metadata['baseline_drift'] = drift

    def _calculate_area_metrics(self, chrom: Chromatogram) -> None:
        if self.global_config.debug:
            self.logger.debug("Calculating area metrics")

        zeros = np.zeros_like(chrom.intensity)
        positive_y = np.where(chrom.intensity > zeros, chrom.intensity, zeros)
        negative_y = np.where(chrom.intensity < zeros, chrom.intensity, zeros)

        total_area = float(np.trapezoid(chrom.intensity, chrom.time))
        positive_area = float(np.trapezoid(positive_y, chrom.time))
        negative_area = float(np.trapezoid(negative_y, chrom.time))

        if self.global_config.debug:
            self.logger.debug(f"Area metrics - total: {total_area:.2f}, positive: {positive_area:.2f}, negative: {negative_area:.2f}")

        chrom.metadata['total_area'] = total_area
        chrom.metadata['positive_area'] = positive_area
        chrom.metadata['negative_area'] = negative_area

    def _calculate_distribution_metrics(self, chrom: Chromatogram) -> None:
        if self.global_config.debug:
            self.logger.debug("Calculating distribution metrics")

        skewness = float(stats.skew(chrom.intensity))
        kurtosis = float(stats.kurtosis(chrom.intensity))
        dynamic_range = float(np.max(chrom.intensity) - np.min(chrom.intensity))

        if self.global_config.debug:
            self.logger.debug(f"Distribution metrics - skewness: {skewness:.2f}, kurtosis: {kurtosis:.2f}, range: {dynamic_range:.2f}")

        chrom.metadata['skewness'] = skewness
        chrom.metadata['kurtosis'] = kurtosis
        chrom.metadata['dynamic_range'] = dynamic_range

    def _calculate_quality_metrics(self, chrom: Chromatogram) -> None:
        if self.global_config.debug:
            self.logger.debug("Calculating quality metrics")

        smoothness = float(np.mean(np.abs(np.diff(chrom.intensity))))
        roughness = float(np.std(np.diff(chrom.intensity)))

        if self.global_config.debug:
            self.logger.debug(f"Quality metrics - smoothness: {smoothness:.2e}, roughness: {roughness:.2e}")

        chrom.metadata['signal_smoothness'] = smoothness
        chrom.metadata['baseline_roughness'] = roughness

    def __call__(self, chrom: Chromatogram) -> Chromatogram:
        return self.analyze_chromatogram(chrom)
