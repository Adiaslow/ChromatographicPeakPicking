# src/chromatographicpeakpicking/core/protocols/loader.py

from typing import Protocol, Any
from chromatographicpeakpicking.core.protocols.reader import Reader

class Loader(Protocol):
    """Protocol for loading data using a reader."""

    def load(self, file_path: str) -> Any:
        """Load data from a specified file path using a reader.

        Args:
            file_path (str): The path from where the data should be loaded.

        Returns:
            The data loaded from the file.
        """
        ...
