# src/chromatographicpeakpicking/infrastructure/metrics/chromatogram_metrics.py
from typing import Any, Dict

class ChromatogramMetrics:
    """Class to store and manage chromatogram metrics."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {}

    def set_metric(self, key: str, value: Any):
        self.metrics[key] = value

    def get_metric(self, key: str) -> Any:
        return self.metrics.get(key)

    def get_all_metrics(self) -> Dict[str, Any]:
        return self.metrics
