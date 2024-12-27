# src/chromatographicpeakpicking/core/protocols/analyzable.py
from abc import ABC, abstractmethod
from typing import Protocol, Any
from ..domain.chromatogram import Chromatogram

class Analyzable(Protocol):
    """Base protocol for all analysis components."""

    @abstractmethod
    def analyze(self, data: Any) -> Any:
        """Perform analysis on input data."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data can be processed."""
        pass
