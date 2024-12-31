# src/chromatographicpeakpicking/analysis/peak/peak_integrator.py
from typing import Dict, Any, Tuple
import numpy as np
from scipy import integrate
from ..protocols.analyzer import Analyzer, AnalysisResult
from ...core.domain.peak import Peak

class PeakIntegrationResult:
    """Results from peak integration."""
    def __init__(self,
                 area: float,
                 baseline_corrected_area: float,
                 metrics: Dict[str, float]):
        self.area = area
        self.baseline_corrected_area = baseline_corrected_area
        self.metrics = metrics

class PeakIntegrator(Analyzer[Peak, PeakIntegrationResult]):
    """Integrates peak area with baseline correction."""

    def __init__(self,
                 time_points: np.ndarray,
                 intensities: np.ndarray,
                 window_size: int = 20):
        self.time_points = time_points
        self.intensities = intensities
        self.window_size = window_size

    async def analyze(self, data: Peak) -> AnalysisResult[PeakIntegrationResult]:
        """Analyze peak area."""
        region = await self._get_peak_region(data)
        baseline = await self._estimate_baseline(region)

        area = await self._integrate_peak(region)
        baseline_area = await self._integrate_baseline(region, baseline)
        corrected_area = area - baseline_area

        metrics = await self._calculate_metrics(region, baseline, area, corrected_area)

        return AnalysisResult(
            result=PeakIntegrationResult(
                area=area,
                baseline_corrected_area=corrected_area,
                metrics=metrics
            ),
            metadata={
                'window_size': self.window_size,
                'integration_method': 'trapezoid'
            },
            execution_time=0.0  # Would be actual execution time
        )

    async def validate(self, data: Peak) -> bool:
        """Validate peak data."""
        return (data.retention_time >= min(self.time_points) and
                data.retention_time <= max(self.time_points))

    async def _get_peak_region(self,
                              peak: Peak) -> Tuple[np.ndarray, np.ndarray]:
        """Extract region around peak."""
        peak_idx = np.argmin(np.abs(self.time_points - peak.retention_time))
        start_idx = max(0, int(peak_idx - self.window_size))
        end_idx = min(len(self.time_points), int(peak_idx + self.window_size))

        return (
            self.time_points[start_idx:end_idx],
            self.intensities[start_idx:end_idx]
        )

    async def _estimate_baseline(self,
                               region: Tuple[np.ndarray, np.ndarray]
                               ) -> np.ndarray:
        """Estimate baseline in peak region."""
        time_points, intensities = region

        # Use endpoints to estimate linear baseline
        baseline_slope = ((intensities[-1] - intensities[0]) /
                         (time_points[-1] - time_points[0]))
        baseline = (intensities[0] +
                   baseline_slope * (time_points - time_points[0]))

        return baseline

    async def _integrate_peak(self,
                            region: Tuple[np.ndarray, np.ndarray]
                            ) -> float:
        """Integrate raw peak area."""
        time_points, intensities = region
        return float(integrate.trapezoid(intensities, time_points))

    async def _integrate_baseline(self,
                                region: Tuple[np.ndarray, np.ndarray],
                                baseline: np.ndarray) -> float:
        """Integrate baseline area."""
        time_points, _ = region
        return float(integrate.trapezoid(baseline, time_points))

    async def _calculate_metrics(self,
                               region: Tuple[np.ndarray, np.ndarray],
                               baseline: np.ndarray,
                               area: float,
                               corrected_area: float) -> Dict[str, float]:
        """Calculate integration quality metrics."""
        _, intensities = region

        return {
            'area_ratio': corrected_area / area if area > 0 else 0.0,
            'baseline_contribution': (area - corrected_area) / area if area > 0 else 0.0,
            'baseline_stability': float(np.std(baseline) / np.mean(baseline))
        }
