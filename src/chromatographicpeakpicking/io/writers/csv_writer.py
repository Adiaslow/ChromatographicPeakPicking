# src/chromatographicpeakpicking/io/writers/csv_writer.py

import os
import pandas as pd

from ...core.protocols import Writer

class CSVWriter(Writer):
    """Class for writing data to CSV files."""

    def __init__(self) -> None:
        super().__init__()

    def write(self, data: pd.DataFrame, path: str) -> None:
        """Write data to a CSV file."""
        data.to_csv(path, index=False)
