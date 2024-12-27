# src/chromatographicpeakpicking/infrastructure/logging/analysis_logger.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import traceback
from pathlib import Path
import json
import uuid

@dataclass
class AnalysisLogger:
    """Logger for analysis operations and performance tracking."""

    log_path: Path
    level: int = logging.INFO
    _logger: logging.Logger = field(init=False)
    _session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _start_time: Optional[datetime] = field(default=None)

    def __post_init__(self):
        """Initialize the logger with file and console handlers."""
        self._logger = logging.getLogger("analysis")
        self._logger.setLevel(self.level)

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(self.level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and above to console

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def log_analysis_start(self, parameters: Dict[str, Any]) -> None:
        """Log the start of an analysis process."""
        self._start_time = datetime.now()
        self._logger.info(
            f"Analysis started - Session ID: {self._session_id}\n"
            f"Parameters: {json.dumps(parameters, indent=2)}"
        )

    def log_analysis_step(self, step: str, metrics: Dict[str, Any]) -> None:
        """Log completion of an analysis step with metrics."""
        self._logger.info(
            f"Step completed - {step}\n"
            f"Metrics: {json.dumps(metrics, indent=2)}"
        )

    def log_analysis_end(self, results: Dict[str, Any]) -> None:
        """Log analysis completion with results and duration."""
        if self._start_time:
            duration = datetime.now() - self._start_time
            self._logger.info(
                f"Analysis completed - Session ID: {self._session_id}\n"
                f"Duration: {duration}\n"
                f"Results: {json.dumps(results, indent=2)}"
            )
        else:
            self._logger.warning(
                "Analysis end logged without corresponding start log"
            )

    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log an error with full traceback and context."""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'session_id': self._session_id
        }

        self._logger.error(
            f"Error occurred - Session ID: {self._session_id}\n"
            f"Error details: {json.dumps(error_info, indent=2)}"
        )

    def log_warning(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log a warning with context."""
        warning_info = {
            'message': message,
            'context': context or {},
            'session_id': self._session_id
        }

        self._logger.warning(
            f"Warning - Session ID: {self._session_id}\n"
            f"Details: {json.dumps(warning_info, indent=2)}"
        )

    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log performance metrics from analysis."""
        self._logger.info(
            f"Performance metrics - Session ID: {self._session_id}\n"
            f"Metrics: {json.dumps(metrics, indent=2)}"
        )

    def log_validation_results(self, results: Dict[str, Any]) -> None:
        """Log validation results from data processing."""
        self._logger.info(
            f"Validation results - Session ID: {self._session_id}\n"
            f"Results: {json.dumps(results, indent=2)}"
        )

    def get_session_id(self) -> str:
        """Return the current session ID."""
        return self._session_id
