# src/chromatographicpeakpicking/core/protocols/detectable.py
"""
This module defines the Detectable protocol for peak detection algorithms.
"""

from typing import Protocol, List
from ..prototypes import (
    Chromatogram,
    Peak
)

class Detectable(Protocol):
    """Protocol for peak detection algorithms."""

    def detect(self, chromatogram: Chromatogram) -> List[Peak]:
        """Detect peaks in a chromatogram."""
        raise NotImplementedError

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate that the chromatogram can be processed."""
        raise NotImplementedError
