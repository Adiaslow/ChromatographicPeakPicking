# src/chromatographicpeakpicking/io/protocols/writer.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pathlib import Path

T = TypeVar('T')

class Writer(ABC, Generic[T]):
    """Base protocol for all writers."""

    @abstractmethod
    async def write(self, data: T, destination: Path) -> None:
        """Write data to a destination."""
        pass
