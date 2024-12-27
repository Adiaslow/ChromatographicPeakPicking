# src/chromatographicpeakpicking/core/protocols/analyzable.py
"""
This module defines the Analyzable protocol for all analysis components.
"""

from typing import Protocol, Any

class Analyzable(Protocol):
    """Base protocol for all analysis components."""

    def analyze(self, data: Any) -> Any:
        """Perform analysis on input data."""
        raise NotImplementedError

    def validate(self, data: Any) -> bool:
        """Validate input data can be processed."""
        raise NotImplementedError
