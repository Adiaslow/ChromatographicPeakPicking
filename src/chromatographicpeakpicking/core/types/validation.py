# src/chromatographicpeakpicking/core/types/validation.py
"""

"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

class ValidationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class ValidationMessage:
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    # context: Dict[str, Any] = field(default_factory=lambda: {})

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    messages: List[ValidationMessage]

    def has_errors(self) -> bool:
        return any(m.level == ValidationLevel.ERROR for m in self.messages)

    def has_warnings(self) -> bool:
        return any(m.level == ValidationLevel.WARNING for m in self.messages)
