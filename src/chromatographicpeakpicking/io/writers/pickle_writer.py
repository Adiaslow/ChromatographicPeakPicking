# src/chromatographicpeakpicking/io/writers/pickle_writter.py

import pandas as pd
import pickle
from typing import Any

from ...core.protocols import Writer

class PickleWriter(Writer):
    def __init__(self) -> None:
        super().__init__()

    def write(self, data: Any, path: str) -> None:
        with open(path, 'wb') as file:
            pickle.dump(data, file)
