# src/chromatographicpeakpicking/analyzers/peak_analyzer.py
from dataclasses import dataclass, field
import numpy as np
from scipy.signal import peak_widths
from scipy.optimize import curve_fit
from typing import List
from src.chromatographicpeakpicking.core.protocols.configurable import Configurable
from src.chromatographicpeakpicking.core.types.config import BaseConfig, ConfigMetadata, ConfigValidation
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.domain.peak import Peak

@dataclass
class PeakAnalyzerConfig(BaseConfig):
    def __init__(self, threshold: float = 0.5):
        super().__init__(metadata=ConfigMetadata(
            name="PeakAnalyzerConfig",
            version="1.0",
            description="Configuration for Peak Analyzer",
            defaults={"threshold": 0.5},
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={"threshold": threshold})

@dataclass
class PeakAnalyzer(Configurable[PeakAnalyzerConfig]):
    config: PeakAnalyzerConfig = field(default_factory=PeakAnalyzerConfig)

    def configure(self, config: PeakAnalyzerConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def get_metadata(self) -> ConfigMetadata:
        return self.config.metadata

    def validate_config(self, config: PeakAnalyzerConfig) -> ValidationResult:
        errors = []
        if config.parameters["threshold"] < 0 or config.parameters["threshold"] > 1:
            errors.append("Threshold must be between 0 and 1.")
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def analyze_peak(self, peak: Peak, chromatogram: Chromatogram) -> Peak:
        x, y = chromatogram.x, chromatogram.y_corrected
        peak = self._calculate_peak_boundaries(x, y, peak)
        peak = self._calculate_peak_width(x, y, peak)
        peak = self._calculate_peak_area(x, y, peak)
        peak = self._calculate_peak_symmetry(y, peak)
        peak = self._calculate_peak_skewness(y, peak)
        peak = self._calculate_peak_prominence(y, peak)
        peak = self._calculate_gaussian_fit(x, y, peak)
        peak = self._calculate_peak_resolution(x, y, peak, chromatogram.peaks)
        peak = self._calculate_peak_score(peak)
        return peak

    @staticmethod
    def _gaussian(x: np.ndarray, amplitude: float, mean: float, std: float) -> np.ndarray:
        """Gaussian function for curve fitting."""
        return amplitude * np.exp(-(x - mean) ** 2 / (2 * std ** 2))

    @staticmethod
    def _calculate_peak_boundaries(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """Calculate peak boundaries by finding the valleys (local minima) on each side of the peak."""
        # Start from peak and move outward
        left = peak['index']
        right = peak['index']

        # Move left until we find a local minimum
        while left > 0 and not (y[left] <= y[left - 1] and y[left] <= y[left + 1]):
            left -= 1

        # Move right until we find a local minimum
        while right < len(y) - 1 and not (y[right] <= y[right - 1] and y[right] <= y[right + 1]):
            right += 1

        # Store boundaries
        peak['left_base_index'], peak['right_base_index'] = left, right
        peak['left_base_time'], peak['right_base_time'] = x[left], x[right]
        return peak

    @staticmethod
    def _calculate_gaussian_fit(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """Calculate how well the peak fits to a Gaussian shape."""
        # Get the peak region
        peak_slice = slice(peak['left_base_index'], peak['right_base_index'] + 1)
        x_peak = x[peak_slice]
        y_peak = y[peak_slice]

        # Background correction - subtract minimum in region
        y_baseline = min(y[peak['left_base_index']], y[peak['right_base_index']])
        y_peak_corrected = y_peak - y_baseline

        try:
            # Estimate parameters
            amplitude = peak['height'] - y_baseline
            mean = peak['time']
            half_max = amplitude / 2
            half_max_indices = np.where(y_peak_corrected >= half_max)[0]
            if len(half_max_indices) >= 2:
                sigma_estimate = (x_peak[half_max_indices[-1]] - x_peak[half_max_indices[0]]) / 2.355
            else:
                sigma_estimate = (x_peak[-1] - x_peak[0]) / 4

            p0 = [amplitude, mean, max(sigma_estimate, 0.1)]
            bounds = (
                [amplitude * 0.5, x_peak[0], sigma_estimate * 0.2],
                [amplitude * 1.5, x_peak[-1], sigma_estimate * 5.0]
            )

            popt, _ = curve_fit(PeakAnalyzer._gaussian, x_peak, y_peak_corrected,
                                p0=p0, bounds=bounds, maxfev=2000)

            y_fit = PeakAnalyzer._gaussian(x_peak, *popt) + y_baseline

            residuals = np.sqrt(np.mean((y_peak - y_fit) ** 2)) / peak['height']
            peak['gaussian_residuals'] = residuals
            peak['gaussian_fit_params'] = {
                'amplitude': popt[0],
                'mean': popt[1],
                'sigma': popt[2],
                'baseline': y_baseline
            }

        except (RuntimeError, ValueError) as e:
            peak['gaussian_residuals'] = 1.0
            peak['gaussian_fit_params'] = {
                'error': str(e)
            }

        return peak

    @staticmethod
    def _calculate_peak_width(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        widths = peak_widths(y, [peak['index']])
        peak['width'] = widths[0][0]
        peak['width_5'] = widths[0][0] * 2.355
        return peak

    @staticmethod
    def _calculate_peak_area(x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        peak['area'] = np.trapz(
            y[peak['left_base_index']:peak['right_base_index']+1],
            x[peak['left_base_index']:peak['right_base_index']+1]
        )
        return peak

    @staticmethod
    def _calculate_peak_symmetry(y: np.ndarray, peak: Peak) -> Peak:
        left = y[peak['left_base_index']:peak['index']+1]
        right = y[peak['index']:peak['right_base_index']+1][::-1]
        min_len = min(len(left), len(right))
        peak['symmetry'] = 1 - np.mean(np.abs(left[-min_len:] - right[-min_len:]) / y[peak['index']])
        return peak

    @staticmethod
    def _calculate_peak_skewness(y: np.ndarray, peak: Peak) -> Peak:
        peak_y = y[peak['left_base_index']:peak['right_base_index']+1]
        peak_y = (peak_y - np.mean(peak_y)) / np.std(peak_y)
        peak['skewness'] = np.mean(peak_y**3)
        return peak

    @staticmethod
    def _calculate_peak_resolution(x: np.ndarray, y: np.ndarray, peak: Peak, peaks: List[Peak]) -> Peak:
        all_peak_indices = [p['index'] for p in peaks]
        if len(all_peak_indices) < 2:
            peak['resolution'] = float('inf')
            return peak

        distances = np.abs(np.array(all_peak_indices) - peak['index'])
        nearest = all_peak_indices[np.argsort(distances)[1]]
        delta_t = abs(x[peak['index']] - x[nearest])
        peak['resolution'] = 2 * delta_t / (peak['width'] + peak_widths(y, [nearest])[0][0])
        return peak

    @staticmethod
    def _calculate_peak_prominence(y: np.ndarray, peak: Peak) -> Peak:
        peak['prominence'] = peak['height'] - np.min([y[peak['left_base_index']], y[peak['right_base_index']]])
        return peak

    @staticmethod
    def _calculate_peak_score(peak: Peak) -> Peak:
        metrics = [
            peak['symmetry'],
            1 / (1 + peak['gaussian_residuals']),
            min(peak['resolution'] / 2, 1),
            1 - abs(peak['skewness']) / 2
        ]

        relative_time = peak['time'] / 60
        time_weight = (relative_time / 0.3) ** 6 if relative_time < 0.3 else 1.0

        peak['score'] = (np.mean(metrics) *
                         peak['prominence'] *
                         peak['area'] *
                         time_weight)
        return peak
