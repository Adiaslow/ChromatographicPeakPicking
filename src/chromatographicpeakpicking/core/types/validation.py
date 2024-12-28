# src/chromatographicpeakpicking/core/types/validation.py
"""
This module defines classes and enums for handling validation results and messages.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ValidationLevel(Enum):
    """Enumeration representing different levels of validation messages."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class ValidationMessage:
    """
    Represents a validation message with a level and message text.

    Attributes:
        level (ValidationLevel): The level of the validation message (INFO, WARNING, ERROR).
        message (str): The text of the validation message.
        field (Optional[str]): The field related to the validation message, if applicable.
    """
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    # context: Dict[str, Any] = field(default_factory=lambda: {})

@dataclass(frozen=True)
class ValidationResult:
    """
    Encapsulates the result of a validation process, including its validity and messages.

    Attributes:
        is_valid (bool): Indicates whether the validation was successful.
        messages (List[ValidationMessage]): A list of validation messages.
    """
    is_valid: bool
    messages: List[ValidationMessage]

    def has_errors(self) -> bool:
        """
        Check if the validation result contains any error messages.

        Returns:
            bool: True if there are error messages, False otherwise.
        """
        return any(m.level == ValidationLevel.ERROR for m in self.messages)

    def has_warnings(self) -> bool:
        """
        Check if the validation result contains any warning messages.

        Returns:
            bool: True if there are warning messages, False otherwise.
        """
        return any(m.level == ValidationLevel.WARNING for m in self.messages)
