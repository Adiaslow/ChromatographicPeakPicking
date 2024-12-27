# src/chromatographicpeakpicking/core/protocols/selectable.py
from typing import Protocol, List
from ..domain.peak import Peak

class PeakSelector(Protocol):
    """Protocol for peak selection algorithms."""

    def select(self, peaks: List[Peak]) -> List[Peak]:
        """Select peaks based on algorithm criteria."""
        ...

    def validate(self, peaks: List[Peak]) -> None:
        """Validate that the peaks can be processed."""
        ...
