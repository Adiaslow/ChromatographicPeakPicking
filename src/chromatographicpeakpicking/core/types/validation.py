# src/chromatographicpeakpicking/core/types/validation.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

class ValidationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class ValidationMessage:
    """
    Immutable validation message.

    Attributes:
        level: Severity level of the validation message
        message: Human-readable validation message
        field: Optional field name this validation applies to
        context: Additional validation context
    """
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    context: Dict[str, Any] = None

@dataclass(frozen=True)
class ValidationResult:
    """
    Immutable result of validation.

    Attributes:
        is_valid: Whether validation passed
        messages: List of validation messages
    """
    is_valid: bool
    messages: List[ValidationMessage]

    def has_errors(self) -> bool:
        """Check if validation produced any errors."""
        return any(m.level == ValidationLevel.ERROR for m in self.messages)

    def has_warnings(self) -> bool:
        """Check if validation produced any warnings."""
        return any(m.level == ValidationLevel.WARNING for m in self.messages)
