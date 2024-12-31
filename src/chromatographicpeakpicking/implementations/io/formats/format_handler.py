# src/chromatographicpeakpicking/io/formats/format_handler.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path

class FormatHandler(ABC):
    """Base class for handling different file formats."""

    @abstractmethod
    async def validate(self, path: Path) -> bool:
        """Validate if file matches expected format."""
        pass

    @abstractmethod
    async def read(self, path: Path) -> Dict[str, Any]:
        """Read data from file in specific format."""
        pass

    @abstractmethod
    async def write(self, data: Dict[str, Any], path: Path) -> None:
        """Write data to file in specific format."""
        pass
