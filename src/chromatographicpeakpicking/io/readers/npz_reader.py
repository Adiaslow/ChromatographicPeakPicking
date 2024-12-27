# src/chromatographicpeakpicking/io/readers/npz_reader.py

import numpy as np
import pandas as pd

from ...core.protocols import Reader

class NPZReader(Reader):
    """Class to read data from a .npz file"""
    def __init__(self) -> None:
        super().__init__()

    def read(self, file_path: str) -> pd.DataFrame:
        """Read data from a .npz file"""
        data = np.load(file_path)
        return pd.DataFrame(data)
