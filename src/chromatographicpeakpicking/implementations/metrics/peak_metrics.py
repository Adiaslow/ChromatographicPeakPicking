
from dataclasses import dataclass, field
from typing import Dict, Optional

from .Imetrics import IMetrics

@dataclass
class PeakMetrics(IMetrics):
    """Implementation of metrics storage for chromatographic peaks.

    Stores various peak-specific metrics including:
        - Time metrics (time, indices)
        - Shape metrics (height, width, symmetry)
        - Area metrics (total area, prominence)
        - Quality metrics (resolution, score)
        - Analysis data (gaussian residuals, approximation curve)
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
