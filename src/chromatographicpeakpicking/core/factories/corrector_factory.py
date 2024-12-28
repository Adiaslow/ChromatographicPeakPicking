# src/chromatographicpeakpicking/core/factories/corrector_factory.py
"""
This module defines the CorrectorFactory class, which is used to create instances of baseline
correctors.
"""
from dataclasses import dataclass, field
from typing import Dict, Type
from ..protocols.correctable import Correctable

@dataclass
class CorrectorFactory:
    """Factory for creating baseline correctors."""

    _correctors: Dict[str, Type[Correctable]] = field(default_factory=dict)

    def register(self, name: str, corrector_class: Type[Correctable]) -> None:
        """Register a new corrector type."""
        self._correctors[name] = corrector_class

    def create(self, name: str, **kwargs) -> Correctable:
        """Create a corrector instance."""
        if name not in self._correctors:
            raise KeyError(f"Unknown corrector type: {name}")
        return self._correctors[name](**kwargs)
