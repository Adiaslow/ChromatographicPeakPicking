# src/chromatographicpeakpicking/core/factories/detector_factory.py
"""
This module defines the DetectorFactory class, which is used to create instances of peak detectors
for chromatographic peak picking.
"""
from dataclasses import dataclass, field
from typing import Dict, Type
from ..protocols.detectable import Detectable

@dataclass
class DetectorFactory:
    """Factory for creating peak detectors."""

    _detectors: Dict[str, Type[Detectable]] = field(default_factory=dict)

    def register(self, name: str, detector_class: Type[Detectable]) -> None:
        """Register a new detector type."""
        self._detectors[name] = detector_class

    def create(self, name: str, **kwargs) -> Detectable:
        """Create a detector instance."""
        if name not in self._detectors:
            raise KeyError(f"Unknown detector type: {name}")
        return self._detectors[name](**kwargs)
