# src/chromatographicpeakpicking/core/protocols/detectable.py
from typing import Protocol, List
from ..domain.chromatogram import Chromatogram
from ..domain.peak import Peak

class PeakDetector(Protocol):
    """Protocol for peak detection algorithms."""

    def detect(self, chromatogram: Chromatogram) -> List[Peak]:
        """Detect peaks in a chromatogram."""
        ...

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate that the chromatogram can be processed."""
        ...
