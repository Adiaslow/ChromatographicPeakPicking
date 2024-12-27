# src/chromatographicpeakpicking/core/errors.py
from enum import Enum
from dataclasses import dataclass

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass(frozen=True)
class ProcessingError:
    severity: ErrorSeverity
    message: str
    source: str
    details: dict
