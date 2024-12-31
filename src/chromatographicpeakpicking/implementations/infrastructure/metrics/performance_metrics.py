# src/chromatographicpeakpicking/infrastructure/metrics/performance_metrics.py

"""
Performance metrics tracking.
"""

import time

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {}

    def start_operation(self, operation_name):
        """
        Start tracking an operation.

        Args:
            operation_name (str): The name of the operation.
        """
        self.metrics[operation_name] = {"start_time": time.time()}

    def end_operation(self, operation_name):
        """
        End tracking an operation and record its duration.

        Args:
            operation_name (str): The name of the operation.
        """
        if operation_name in self.metrics and "start_time" in self.metrics[operation_name]:
            start_time = self.metrics[operation_name]["start_time"]
            self.metrics[operation_name]["duration"] = time.time() - start_time

    def get_operation_stats(self, operation_name):
        """
        Retrieve the statistics of a specific operation.

        Args:
            operation_name (str): The name of the operation.
        """
        return self.metrics.get(operation_name, {})
