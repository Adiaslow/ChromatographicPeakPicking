# src/chromatographicpeakpicking/core/factories/corrector_factory.py
from dataclasses import dataclass, field
from typing import Dict, Type
from ..protocols.correctable import BaselineCorrector

@dataclass
class CorrectorFactory:
    """Factory for creating baseline correctors."""

    _correctors: Dict[str, Type[BaselineCorrector]] = field(default_factory=dict)

    def register(self, name: str, corrector_class: Type[BaselineCorrector]) -> None:
        """Register a new corrector type."""
        self._correctors[name] = corrector_class

    def create(self, name: str, **kwargs) -> BaselineCorrector:
        """Create a corrector instance."""
        if name not in self._correctors:
            raise KeyError(f"Unknown corrector type: {name}")
        return self._correctors[name](**kwargs)
