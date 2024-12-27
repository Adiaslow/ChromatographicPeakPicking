# src/chromatographicpeakpicking/io/protocols/reader.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from pathlib import Path

T = TypeVar('T')

class Reader(ABC, Generic[T]):
    """Base protocol for all readers."""

    @abstractmethod
    async def read(self, source: Path) -> T:
        """Read data from a source."""
        pass
