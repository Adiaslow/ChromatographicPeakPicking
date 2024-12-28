# src/chromatographicpeakpicking/core/protocols/visualizable.py
"""
This module defines the Visualizable protocol for visualization components.
"""

from typing import Protocol, Any
from pathlib import Path

class Visualizable(Protocol):
    """Protocol for visualization components."""

    def visualize(self, data: Any) -> Any:
        """
        Create visualization of data.

        Args:
            data (Any): The data to be visualized.

        Returns:
            Any: The visualization object.
        """
        raise NotImplementedError

    def save(self, path: Path) -> None:
        """
        Save visualization to file.

        Args:
            path (Path): The file path where the visualization will be saved.
        """
        raise NotImplementedError
