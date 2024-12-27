# src/chromatographicpeakpicking/analysis/chromatogram/peak_detector.py
from typing import List, Dict, Any
import numpy as np
from scipy.signal import find_peaks
from ..protocols.analyzer import Analyzer, AnalysisResult
from ...core.domain.chromatogram import Chromatogram
from ...core.domain.peak import Peak

class PeakDetectionResult:
    """Results from peak detection."""
    def __init__(self, peaks: List[Peak], metrics: Dict[str, float]):
        self.peaks = peaks
        self.metrics = metrics

class PeakDetector(Analyzer[Chromatogram, PeakDetectionResult]):
    """Detects peaks in chromatogram data."""

    def __init__(self,
                 height_threshold: float = 0.1,
                 prominence_threshold: float = 0.2,
                 width_threshold: float = 5):
        self.height_threshold = height_threshold
        self.prominence_threshold = prominence_threshold
        self.width_threshold = width_threshold

    async def analyze(self, data: Chromatogram) -> AnalysisResult[PeakDetectionResult]:
        """Detect peaks in chromatogram."""
        peak_indices, properties = await self._find_peaks(data)
        peaks = await self._create_peaks(data, peak_indices, properties)
        metrics = await self._calculate_metrics(peaks)

        return AnalysisResult(
            result=PeakDetectionResult(peaks, metrics),
            metadata={
                'height_threshold': self.height_threshold,
                'prominence_threshold': self.prominence_threshold,
                'width_threshold': self.width_threshold
            },
            execution_time=0.0  # Would be actual execution time
        )

    async def validate(self, data: Chromatogram) -> bool:
        """Validate chromatogram data."""
        return len(data.time_points) > 0 and len(data.intensities) > 0

    async def _find_peaks(self,
                         data: Chromatogram) -> tuple[np.ndarray, Dict[str, Any]]:
        """Find peaks using scipy.signal."""
        return find_peaks(
            data.intensities,
            height=self.height_threshold,
            prominence=self.prominence_threshold,
            width=self.width_threshold
        )

    async def _create_peaks(self,
                           data: Chromatogram,
                           indices: np.ndarray,
                           properties: Dict[str, Any]) -> List[Peak]:
        """Create Peak objects from detected peaks."""
        peaks = []
        for i, idx in enumerate(indices):
            peak = Peak(
                retention_time=float(data.time_points[idx]),
                height=float(data.intensities[idx]),
                area=float(properties.get('width_heights', [0])[i]),
                metadata={
                    'prominence': float(properties.get('prominences', [0])[i]),
                    'width': float(properties.get('widths', [0])[i])
                }
            )
            peaks.append(peak)
        return peaks

    async def _calculate_metrics(self, peaks: List[Peak]) -> Dict[str, float]:
        """Calculate detection metrics."""
        return {
            'num_peaks': len(peaks),
            'avg_height': np.mean([p.height for p in peaks]),
            'avg_width': np.mean([p.metadata.get('width', 0) for p in peaks])
        }
