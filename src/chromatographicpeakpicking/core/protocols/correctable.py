# src/chromatographicpeakpicking/core/protocols/correctable.py
"""
This module defines the BaselineCorrector protocol for baseline correction algorithms.
"""

from typing import Protocol
from ..domain.chromatogram import Chromatogram

class BaselineCorrector(Protocol):
    """Protocol for baseline correction algorithms."""

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply baseline correction to a chromatogram."""
        raise NotImplementedError

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate that the chromatogram can be processed."""
        raise NotImplementedError
