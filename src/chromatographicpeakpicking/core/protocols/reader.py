# src/chromatographicpeakpicking/core/protocols/reader.py

from typing import Protocol, Any

class Reader(Protocol):
    """Protocol for reading data."""

    def read_data(self, file_path: str) -> Any:
        """Read data from a specified file path.

        Args:
            file_path (str): The path from where the data should be read.

        Returns:
            The data read from the file.
        """
        ...
