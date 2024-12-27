# src/chromatographicpeakpicking/infrastructure/metrics/performance_metrics.py
from dataclasses import dataclass, field
from typing import Dict, List
import time
from datetime import datetime

@dataclass
class OperationMetrics:
    """Metrics for a single operation."""
    start_time: float
    end_time: float = field(default=0.0)
    duration: float = field(default=0.0)

@dataclass
class MetricValue:
    """A single metric measurement."""
    value: float
    timestamp: datetime

class PerformanceMetrics:
    """Handles collection and aggregation of performance metrics."""

    def __init__(self):
        self._operations: Dict[str, List[OperationMetrics]] = {}
        self._metrics: Dict[str, List[MetricValue]] = {}

    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation.

        Args:
            operation_name: Name of the operation to time
        """
        if operation_name not in self._operations:
            self._operations[operation_name] = []

        self._operations[operation_name].append(
            OperationMetrics(start_time=time.perf_counter())
        )

    def end_operation(self, operation_name: str) -> None:
        """End timing an operation.

        Args:
            operation_name: Name of the operation to stop timing
        """
        if operation_name not in self._operations:
            raise ValueError(f"Operation {operation_name} was never started")

        current_op = self._operations[operation_name][-1]
        current_op.end_time = time.perf_counter()
        current_op.duration = current_op.end_time - current_op.start_time

    def record_metric(self, metric_name: str, value: float) -> None:
        """Record a metric value.

        Args:
            metric_name: Name of the metric
            value: Value to record
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []

        self._metrics[metric_name].append(
            MetricValue(value=value, timestamp=datetime.now())
        )

    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """Get statistics for an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Dictionary containing min, max, avg duration
        """
        if operation_name not in self._operations:
            return {}

        durations = [op.duration for op in self._operations[operation_name]]
        return {
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_duration': sum(durations) / len(durations)
        }

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary containing min, max, avg values
        """
        if metric_name not in self._metrics:
            return {}

        values = [m.value for m in self._metrics[metric_name]]
        return {
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values)
        }
