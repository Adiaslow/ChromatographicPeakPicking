# src/chromatographicpeakpicking/io/writers/hdf5_writer.py

import pandas as pd

from ...core.protocols import Writer

class HDF5Writer(Writer):
    def __init__(self) -> None:
        super().__init__()

    def write(self, data: pd.DataFrame, path: str) -> None:
        ...
