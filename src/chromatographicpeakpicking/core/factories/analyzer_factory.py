# src/chromatographicpeakpicking/core/factories/analyzer_factory.py
"""
This module defines the AnalyzerFactory class, which is used to create instances of analysis components for chromatographic peak picking.
"""
from dataclasses import dataclass, field
from typing import Dict, Type, Any
from ..protocols.analyzable import Analyzable

@dataclass
class AnalyzerFactory:
    """Factory for creating analysis components."""

    _analyzers: Dict[str, Type[Analyzable]] = field(default_factory=dict)

    def register(self, name: str, analyzer_class: Type[Analyzable]) -> None:
        """Register a new analyzer type."""
        self._analyzers[name] = analyzer_class

    def create(self, name: str, **kwargs: Any) -> Analyzable:
        """Create an analyzer instance."""
        if name not in self._analyzers:
            raise KeyError(f"Unknown analyzer type: {name}")
        return self._analyzers[name](**kwargs)
