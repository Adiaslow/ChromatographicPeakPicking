# src/chromatographicpeakpicking/core/protocols/error_handler.py
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
        ...

    def set_severity_threshold(self, threshold: ErrorSeverity) -> None:
        """
        Set minimum severity level for error handling.

        Args:
            threshold: Minimum severity to handle
        """
        pass

class ErrorCollection(Protocol):
    """Protocol for collecting errors during processing."""

    def add_error(self, error: ProcessingError) -> None:
        """Add an error to the collection."""
        ...

    def get_errors(self, min_severity: Optional[ErrorSeverity] = None) -> List[ProcessingError]:
        """Get collected errors, optionally filtered by severity."""
        ...

    def clear(self) -> None:
        """Clear all collected errors."""
        ...
