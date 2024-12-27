# src/chromatographicpeakpicking/core/protocols/error_handler.py
"""
This module defines protocols for error handling strategies and error collection
during processing.
"""

from typing import List, Optional, Protocol
from ..types.errors import ProcessingError, ErrorSeverity

class ErrorHandler(Protocol):
    """Protocol for error handling strategies."""

    def handle_error(self, error: ProcessingError) -> bool:
        """
        Handle a processing error.

        Args:
            error: The error that occurred

        Returns:
            bool: True if processing should continue, False if it should stop
        """
        raise NotImplementedError

    def set_severity_threshold(self, threshold: ErrorSeverity) -> None:
        """
        Set minimum severity level for error handling.

        Args:
            threshold: Minimum severity to handle
        """
        raise NotImplementedError

class ErrorCollection(Protocol):
    """Protocol for collecting errors during processing."""

    def add_error(self, error: ProcessingError) -> None:
        """Add an error to the collection."""
        raise NotImplementedError

    def get_errors(self, min_severity: Optional[ErrorSeverity] = None) -> List[ProcessingError]:
        """Get collected errors, optionally filtered by severity."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all collected errors."""
        raise NotImplementedError
