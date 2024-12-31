# src/chromatographicpeakpicking/io/formats/csv_format.py
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from .format_handler import FormatHandler

class CSVFormatHandler(FormatHandler):
    """Handles CSV file format operations."""

    async def validate(self, path: Path) -> bool:
        """Validate if file is valid CSV."""
        if not path.suffix.lower() == '.csv':
            return False

        try:
            pd.read_csv(path, nrows=1)
            return True
        except Exception:
            return False

    async def read(self, path: Path) -> Dict[str, Any]:
        """Read CSV file into dictionary."""
        df = pd.read_csv(path)
        return {
            'data': df.to_dict('records'),
            'columns': list(df.columns),
            'format': 'csv'
        }

    async def write(self, data: Dict[str, Any], path: Path) -> None:
        """Write dictionary to CSV file."""
        df = pd.DataFrame(data['data'])
        df.to_csv(path, index=False)
