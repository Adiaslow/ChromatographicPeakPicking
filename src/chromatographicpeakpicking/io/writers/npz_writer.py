# src/chromatographicpeakpicking/io/writers/npz_writer.py

import pandas as pd

from ...core.protocols import Writer

class NPZWriter(Writer):
    """Writer for NumPy NPZ files"""
    def __init__(self) -> None:
        super().__init__()

    def write(self, data: pd.DataFrame, path: str) -> None:
        data.to_numpy().dump(path)
