# src/chromatographicpeakpicking/infrastructure/logging/performance_logger.py

"""
Logger for performance metrics.
"""

class PerformanceLogger:
    def __init__(self):
        self.operations = []

    def log_operation(self, operation_name, duration):
        """
        Log a performance operation.

        Args:
            operation_name (str): The name of the operation.
            duration (float): The duration of the operation in seconds.
        """
        self.operations.append((operation_name, duration))

    def get_operation_history(self):
        """
        Retrieve the history of logged operations.
        """
        return self.operations

    def get_average_duration(self, operation_name):
        """
        Calculate the average duration of a specific operation.

        Args:
            operation_name (str): The name of the operation.
        """
        durations = [duration for name, duration in self.operations if name == operation_name]
        return sum(durations) / len(durations) if durations else 0.0
