# src/chromatographicpeakpicking/io/writers/tsv_writer.py

from ...core.protocols import Writer

class TSVWriter(Writer):
    """Tab-separated values writer"""

    def __init__(self) -> None:
        super().__init__()

    def write(self, data: dict, path: str) -> None:
        """Write data to a tab-separated values file."""
        with open(path, 'w') as f:
            for key, value in data.items():
                f.write(f"{key}\t{value}\n")
