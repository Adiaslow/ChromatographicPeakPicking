# src/chromatographicpeakpicking/io/writers/xlsx_writer.py

import pandas as pd

from ...core.protocols import Writer

class XLSXWriter(Writer):
    """XLSX writer"""
    def __init__(self) -> None:
        super().__init__()

    def write(self, data: pd.DataFrame, filename: str) -> None:
        """Write data to XLSX file."""
        data.to_excel(filename, index=False)
