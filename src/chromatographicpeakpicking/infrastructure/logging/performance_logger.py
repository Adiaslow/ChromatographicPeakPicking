# src/chromatographicpeakpicking/infrastructure/logging/performance_logger.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

@dataclass
class PerformanceLog:
    """Performance log entry."""
    operation: str
    duration: float
    timestamp: datetime
    metadata: Optional[Dict] = None

class PerformanceLogger:
    """Logger for tracking performance metrics."""

    def __init__(self, log_file: str = "performance.log"):
        self._logger = logging.getLogger("performance")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._entries: List[PerformanceLog] = []

    def log_operation(self,
                     operation: str,
                     duration: float,
                     metadata: Optional[Dict] = None) -> None:
        """Log a performance metric.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            metadata: Optional metadata about the operation
        """
        entry = PerformanceLog(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self._entries.append(entry)

        log_data = {
            'operation': operation,
            'duration': duration,
            'timestamp': entry.timestamp.isoformat(),
            'metadata': metadata
        }
        self._logger.info(json.dumps(log_data))

    def get_operation_history(self, operation: str) -> List[PerformanceLog]:
        """Get history for an operation.

        Args:
            operation: Operation name

        Returns:
            List of performance logs for the operation
        """
        return [e for e in self._entries if e.operation == operation]

    def get_average_duration(self, operation: str) -> float:
        """Get average duration for an operation.

        Args:
            operation: Operation name

        Returns:
            Average duration in seconds
        """
        logs = self.get_operation_history(operation)
        if not logs:
            return 0.0
        return sum(log.duration for log in logs) / len(logs)
