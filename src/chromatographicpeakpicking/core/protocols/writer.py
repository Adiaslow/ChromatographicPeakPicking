# src/chromatographicpeakpicking/core/protocols/writer.py

from typing import Protocol

class Writer(Protocol):
    """Protocol for writing data."""

    def write_data(self, data, file_path: str) -> None:
        """Write data to a specified file path.

        Args:
            data: The data to be written.
            file_path (str): The path where the data should be written.
        """
        ...
