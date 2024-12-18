from dataclasses import dataclass, field
from typing import Dict, Optional
from .Imetrics import IMetrics

@dataclass
class ChromatogramMetrics(IMetrics):
    """Implementation of metrics storage for chromatograms.

    Stores various chromatogram-specific metrics including:
        - Noise metrics (noise level, SNR)
        - Baseline metrics (mean, drift)
        - Area metrics (total, positive, negative)
        - Distribution metrics (skewness, kurtosis)
        - Quality metrics (smoothness, roughness)
    """
    metrics: Dict[str, float] = field(default_factory=dict)

    def get_metric(self, metric_name: str) -> Optional[float]:
        """Get a specific metric value by name.

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            Value of the requested metric or None if not found
        """
        return self.metrics.get(metric_name)

    def set_metric(self, metric_name: str, value: float) -> None:
        """Set a specific metric value.

        Args:
            metric_name: Name of the metric to set
            value: Value to set for the metric
        """
        self.metrics[metric_name] = value

    def get_all_metrics(self) -> Dict[str, float]:
        """Get all stored metrics.

        Returns:
            Dictionary containing all stored metrics
        """
        return self.metrics.copy()
