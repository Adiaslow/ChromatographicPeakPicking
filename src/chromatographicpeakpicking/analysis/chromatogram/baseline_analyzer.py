# src/chromatographicpeakpicking/analysis/chromatogram/baseline_analyzer.py
from typing import Dict, Any, List
import numpy as np
from ..protocols.analyzer import Analyzer, AnalysisResult
from ...core.domain.chromatogram import Chromatogram

class BaselineAnalysisResult:
    """Results from baseline analysis."""
    def __init__(self, baseline: np.ndarray, metrics: Dict[str, float]):
        self.baseline = baseline
        self.metrics = metrics

class BaselineAnalyzer(Analyzer[Chromatogram, BaselineAnalysisResult]):
    """Analyzes chromatogram baseline characteristics."""

    async def analyze(self, data: Chromatogram) -> AnalysisResult[BaselineAnalysisResult]:
        """Analyze baseline of chromatogram."""
        baseline = await self._estimate_baseline(data)
        metrics = await self._calculate_metrics(data, baseline)

        return AnalysisResult(
            result=BaselineAnalysisResult(baseline, metrics),
            metadata={'method': 'moving_average'},
            execution_time=0.0  # Would be actual execution time
        )

    async def validate(self, data: Chromatogram) -> bool:
        """Validate chromatogram data."""
        return len(data.time_points) > 0 and len(data.intensities) > 0

    async def _estimate_baseline(self, data: Chromatogram) -> np.ndarray:
        """Estimate baseline using moving average."""
        window = 50  # Would be configurable
        return np.convolve(data.intensities,
                          np.ones(window)/window,
                          mode='same')

    async def _calculate_metrics(self,
                               data: Chromatogram,
                               baseline: np.ndarray) -> Dict[str, float]:
        """Calculate baseline metrics."""
        return {
            'baseline_mean': float(np.mean(baseline)),
            'baseline_std': float(np.std(baseline)),
            'baseline_drift': float(baseline[-1] - baseline[0])
        }
