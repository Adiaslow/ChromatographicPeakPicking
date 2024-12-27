# src/chromatographicpeakpicking/core/protocols/serializable.py
from typing import Protocol, Any, Dict

class Serializable(Protocol):
    """Protocol for serializable objects."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """Create object from dictionary."""
        ...
