# src/chromatographicpeakpicking/core/protocols/parseable.py
"""
This module defines the Parseable protocol for components that can be parsed from raw data.
"""

from typing import Protocol, Any

class Parseable(Protocol):
    """Protocol for components that can be parsed from raw data."""

    def parse(self, raw_data: Any) -> None:
        """
        Parse the component from raw data.

        Args:
            raw_data (Any): The raw data to parse the component from.
        """
        raise NotImplementedError

    def validate(self, raw_data: Any) -> None:
        """
        Validate that the raw data can be parsed into the component.

        Args:
            raw_data (Any): The raw data to be validated.

        Raises:
            ValidationError: If the raw data is not valid for parsing.
        """
        raise NotImplementedError
