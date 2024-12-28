# src/chromatographicpeakpicking/core/protocols/serializable.py
"""
This module defines the Serializable protocol for serializable objects.
"""

from typing import Protocol, Any, Dict

class Serializable(Protocol):
    """Protocol for serializable objects."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation of the object.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """
        Create object from dictionary.

        Args:
            data (Dict[str, Any]): The dictionary data to create the object from.

        Returns:
            Serializable: A new instance of the class.
        """
        raise NotImplementedError
