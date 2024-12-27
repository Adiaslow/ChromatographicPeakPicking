# src/chromatographicpeakpicking/io/formats/excel_format.py
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from .format_handler import FormatHandler

class ExcelFormatHandler(FormatHandler):
    """Handles Excel file format operations."""

    async def validate(self, path: Path) -> bool:
        """Validate if file is valid Excel."""
        if path.suffix.lower() not in ['.xls', '.xlsx']:
            return False

        try:
            pd.read_excel(path, nrows=1)
            return True
        except Exception:
            return False

    async def read(self, path: Path) -> Dict[str, Any]:
        """Read Excel file into dictionary."""
        df = pd.read_excel(path)
        return {
            'data': df.to_dict('records'),
            'columns': list(df.columns),
            'format': 'excel'
        }

    async def write(self, data: Dict[str, Any], path: Path) -> None:
        """Write dictionary to Excel file."""
        df = pd.DataFrame(data['data'])
        df.to_excel(path, index=False)
