# src/chromatographicpeakpicking/core/protocols/visualizable.py
from typing import Protocol, Any
from pathlib import Path

class Visualizable(Protocol):
    """Protocol for visualization components."""

    def visualize(self, data: Any) -> Any:
        """Create visualization of data."""
        ...

    def save(self, path: Path) -> None:
        """Save visualization to file."""
        ...
