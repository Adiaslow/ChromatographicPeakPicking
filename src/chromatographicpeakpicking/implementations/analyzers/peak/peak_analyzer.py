# src/chromatographicpeakpicking/analysis/peak/peak_analyzer.py
from typing import Dict, Any, Optional
import numpy as np
from scipy.optimize import curve_fit
from ..protocols.analyzer import Analyzer, AnalysisResult
from ...core.domain.peak import Peak

class PeakAnalysisResult:
    """Results from peak analysis."""
    def __init__(self,
                 peak: Peak,
                 fit_params: Dict[str, float],
                 quality_metrics: Dict[str, float]):
        self.peak = peak
        self.fit_params = fit_params
        self.quality_metrics = quality_metrics

class PeakAnalyzer(Analyzer[Peak, PeakAnalysisResult]):
    """Analyzes individual peak characteristics."""

    def __init__(self, time_points: np.ndarray, intensities: np.ndarray):
        self.time_points = time_points
        self.intensities = intensities

    async def analyze(self, data: Peak) -> AnalysisResult[PeakAnalysisResult]:
        """Analyze a single peak."""
        fit_params = await self._fit_gaussian(data)
        quality_metrics = await self._calculate_quality_metrics(data, fit_params)

        return AnalysisResult(
            result=PeakAnalysisResult(data, fit_params, quality_metrics),
            metadata={'analysis_type': 'gaussian_fit'},
            execution_time=0.0  # Would be actual execution time
        )

    async def validate(self, data: Peak) -> bool:
        """Validate peak data."""
        return (data.retention_time >= min(self.time_points) and
                data.retention_time <= max(self.time_points))

    async def _fit_gaussian(self, peak: Peak) -> Dict[str, float]:
        """Fit Gaussian to peak."""
        def gaussian(x: np.ndarray,
                    amplitude: float,
                    mean: float,
                    std: float) -> np.ndarray:
            return amplitude * np.exp(-(x - mean)**2 / (2 * std**2))

        # Get region around peak
        window = 20  # Would be configurable
        peak_idx = np.argmin(np.abs(self.time_points - peak.retention_time))
        start_idx = max(0, int(peak_idx - window))
        end_idx = min(len(self.time_points), int(peak_idx + window))

        x = self.time_points[start_idx:end_idx]
        y = self.intensities[start_idx:end_idx]

        try:
            popt, _ = curve_fit(gaussian, x, y,
                              p0=[peak.height, peak.retention_time, 1.0])
            return {
                'amplitude': float(popt[0]),
                'mean': float(popt[1]),
                'std': float(popt[2])
            }
        except RuntimeError:
            return {
                'amplitude': peak.height,
                'mean': peak.retention_time,
                'std': 1.0
            }

    async def _calculate_quality_metrics(self,
                                      peak: Peak,
                                      fit_params: Dict[str, float]
                                      ) -> Dict[str, float]:
        """Calculate peak quality metrics."""
        # Get region around peak
        window = 20  # Would be configurable
        peak_idx = np.argmin(np.abs(self.time_points - peak.retention_time))
        start_idx = max(0, int(peak_idx - window))
        end_idx = min(len(self.time_points), int(peak_idx + window))

        # Calculate metrics
        signal = self.intensities[start_idx:end_idx]
        noise = np.std(signal - np.mean(signal))

        return {
            'signal_to_noise': float(peak.height / noise if noise > 0 else 0.0),
            'gaussian_r2': self._calculate_r2(
                self.time_points[start_idx:end_idx],
                signal,
                fit_params
            ),
            'peak_symmetry': self._calculate_symmetry(signal),
            'peak_capacity': self._calculate_capacity(fit_params['std'])
        }

    def _calculate_r2(self,
                     x: np.ndarray,
                     y: np.ndarray,
                     fit_params: Dict[str, float]) -> float:
        """Calculate R² for Gaussian fit."""
        def gaussian(x: np.ndarray) -> np.ndarray:
            return fit_params['amplitude'] * np.exp(
                -(x - fit_params['mean'])**2 / (2 * fit_params['std']**2)
            )

        y_pred = gaussian(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    def _calculate_symmetry(self, signal: np.ndarray) -> float:
        """Calculate peak symmetry."""
        peak_idx = np.argmax(signal)
        left_half = signal[:peak_idx]
        right_half = signal[peak_idx:]

        # Interpolate to same length if necessary
        if len(left_half) != len(right_half):
            target_length = min(len(left_half), len(right_half))
            left_half = np.interp(
                np.linspace(0, 1, target_length),
                np.linspace(0, 1, len(left_half)),
                left_half
            )
            right_half = np.interp(
                np.linspace(0, 1, target_length),
                np.linspace(0, 1, len(right_half)),
                right_half
            )

        return np.sum(np.abs(left_half - np.flip(right_half))) / len(left_half)

    def _calculate_capacity(self, std: float) -> float:
        """Calculate peak capacity."""
        return (max(self.time_points) - min(self.time_points)) / (4 * std)
