# src/chromatographicpeakpicking/core/types/errors.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass(frozen=True)
class ProcessingError:
    """
    Immutable container for processing errors.

    Attributes:
        severity: The severity level of the error
        message: Human-readable error message
        source: Component/stage that generated the error
        details: Additional error context and data
    """
    severity: ErrorSeverity
    message: str
    source: str
    details: Dict[str, Any]

class PipelineError(Exception):
    """Base exception for pipeline-related errors."""
    def __init__(self, error: ProcessingError):
        self.error = error
        super().__init__(error.message)

class ValidationError(PipelineError):
    """Raised when input validation fails."""
    pass

class ConfigurationError(PipelineError):
    """Raised when component configuration is invalid."""
    pass

class ProcessingError(PipelineError):
    """Raised when pipeline processing fails."""
    pass
