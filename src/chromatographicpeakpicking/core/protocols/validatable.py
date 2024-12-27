# src/chromatographicpeakpicking/core/protocols/validatable.py
from typing import Protocol, Any, List

class ValidationError:
    """Represents a validation error."""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code

class Validatable(Protocol):
    """Protocol for components that can be validated."""

    def validate(self) -> List[ValidationError]:
        """Validate the component state."""
        ...

    def is_valid(self) -> bool:
        """Check if component is valid."""
        ...
