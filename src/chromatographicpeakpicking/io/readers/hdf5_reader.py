# src/chromatographicpeakpicking/io/readers/hdf5_reader.py

import h5py
import pandas as pd

from ...core.protocols import Reader

class HDF5Reader(Reader):
    def __init__(self):
        super().__init__()

    def read(self, file_path: str) -> pd.DataFrame:
        with h5py.File(file_path, 'r') as file:
            data = file['data'][:]
            columns = file['columns'][:].astype(str)
            return pd.DataFrame(data, columns=columns)
