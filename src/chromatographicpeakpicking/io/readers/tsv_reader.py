# src/chromatographicpeakpicking/io/readers/tsv_reader.py

import pandas as pd

from ...core.protocols import Reader

class TSVReader(Reader):
    """Reads data from a TSV file"""
    def __init__(self) -> None:
        super().__init__()

    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path, sep="\t")
