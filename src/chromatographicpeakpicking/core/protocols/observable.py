# src/chromatographicpeakpicking/core/protocols/observable.py
"""
This module defines protocols for observable components and observers that monitor
analysis progress.
"""

from typing import Protocol
from dataclasses import dataclass

@dataclass
class AnalysisEvent:
    """Event data for analysis updates."""
    stage: str
    progress: float
    message: str = ""

class Observer(Protocol):
    """Protocol for observers of analysis progress."""

    def update(self, event: AnalysisEvent) -> None:
        """Handle analysis progress updates."""
        raise NotImplementedError


class Observable(Protocol):
    """Protocol for observable components."""

    def add_observer(self, observer: Observer) -> None:
        """Add an observer."""
        raise NotImplementedError

    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer."""
        raise NotImplementedError

    def notify_observers(self, event: AnalysisEvent) -> None:
        """Notify all observers."""
        raise NotImplementedError
