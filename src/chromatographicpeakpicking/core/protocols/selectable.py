# src/chromatographicpeakpicking/core/protocols/selectable.py
"""
This module defines the PeakSelector protocol for peak selection algorithms.
"""

from typing import Protocol, List
from ..domain.peak import Peak

class PeakSelector(Protocol):
    """Protocol for peak selection algorithms."""

    def select(self, peaks: List[Peak]) -> List[Peak]:
        """
        Select peaks based on algorithm criteria.

        Args:
            peaks (List[Peak]): A list of peaks to be processed.

        Returns:
            List[Peak]: A list of selected peaks.
        """
        raise NotImplementedError

    def validate(self, peaks: List[Peak]) -> None:
        """
        Validate that the peaks can be processed.

        Args:
            peaks (List[Peak]): A list of peaks to be validated.

        Raises:
            ValidationError: If the peaks are not valid for processing.
        """
        raise NotImplementedError
