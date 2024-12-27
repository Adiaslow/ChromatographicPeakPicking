# src/chromatographicpeakpicking/io/readers/csv_reader.py

import pandas as pd

from ...core.protocols import Reader

class CSVReader(Reader):
    """Reads data from a CSV file"""
    def __init__(self) -> None:
        super().__init__()

    def read(self, file_path: str) -> pd.DataFrame:
        """Reads data from a CSV file"""
        return pd.read_csv(file_path)
