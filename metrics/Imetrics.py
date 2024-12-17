from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class IMetrics(ABC):
    """Abstract base class for metrics storage.

    This interface defines the basic structure for metrics storage
    and access, ensuring consistent implementation across different metric types.
    """
    metrics: Dict[str, float] = field(default_factory=dict)


    def get_metric(self, metric_name: str) -> Optional[float]:
        """Get a specific metric value by name."""
        return self.metrics.get(metric_name)


    def set_metric(self, metric_name: str, value: float) -> None:
        """Set a specific metric value."""
        self.metrics[metric_name] = value


    def get_all_metrics(self) -> Dict[str, float]:
        """Get all stored metrics."""
        return self.metrics.copy()
