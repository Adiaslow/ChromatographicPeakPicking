# src/chromatographicpeakpicking/core/protocols/validatable.py
"""
This module defines the Validatable protocol for components that can be validated.
"""

from typing import Protocol, List

class ValidationError:
    """Represents a validation error."""

    def __init__(self, message: str, code: str = ""):
        """
        Initialize a ValidationError.

        Args:
            message (str): The error message.
            code (str, optional): An optional code for the error.
        """
        self.message = message
        self.code = code

class Validatable(Protocol):
    """Protocol for components that can be validated."""

    def validate(self) -> List[ValidationError]:
        """
        Validate the component state.

        Returns:
            List[ValidationError]: A list of validation errors, if any.
        """
        raise NotImplementedError

    def is_valid(self) -> bool:
        """
        Check if the component is valid.

        Returns:
            bool: True if the component is valid, False otherwise.
        """
        raise NotImplementedError
