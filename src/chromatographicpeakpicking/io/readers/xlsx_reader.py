# src/chromatographicpeakpicking/io/readers/xlsx_reader.py

import pandas as pd

from ...core.protocols import Reader

class XLSXReader:
    """Class for reading data from XLSX files"""
    def __init__(self) -> None:
        super().__init__()

    def read(self, file_path: str) -> pd.DataFrame:
        """Read data from an XLSX file"""
        return pd.read_excel(file_path)
