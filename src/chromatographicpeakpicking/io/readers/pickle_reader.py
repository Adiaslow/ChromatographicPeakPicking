# src/chromatographicpeakpicking/io/readers/pickle_reader.py

import pandas as pd
import pickle

from ...core.protocols import Reader

class PickleReader(Reader):
    def __init__(self) -> None:
        super().__init__()

    def read(self, path: str) -> pd.DataFrame:
        with open(path, "rb") as f:
            data = pickle.load(f)
        return data
