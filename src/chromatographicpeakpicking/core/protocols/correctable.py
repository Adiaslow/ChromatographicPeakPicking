# src/chromatographicpeakpicking/core/protocols/correctable.py
from typing import Protocol
from ..domain.chromatogram import Chromatogram

class BaselineCorrector(Protocol):
    """Protocol for baseline correction algorithms."""

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply baseline correction to a chromatogram."""
        ...

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate that the chromatogram can be processed."""
        ...
