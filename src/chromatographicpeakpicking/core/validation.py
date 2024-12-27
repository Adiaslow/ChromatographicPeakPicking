# src/chromatographicpeakpicking/core/validation.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ValidationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class ValidationMessage:
    level: ValidationLevel
    message: str
    field: Optional[str] = None

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    messages: List[ValidationMessage]
