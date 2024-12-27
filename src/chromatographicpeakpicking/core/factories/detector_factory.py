# src/chromatographicpeakpicking/core/factories/detector_factory.py
from dataclasses import dataclass, field
from typing import Dict, Type
from ..protocols.detectable import PeakDetector

@dataclass
class DetectorFactory:
    """Factory for creating peak detectors."""

    _detectors: Dict[str, Type[PeakDetector]] = field(default_factory=dict)

    def register(self, name: str, detector_class: Type[PeakDetector]) -> None:
        """Register a new detector type."""
        self._detectors[name] = detector_class

    def create(self, name: str, **kwargs) -> PeakDetector:
        """Create a detector instance."""
        if name not in self._detectors:
            raise KeyError(f"Unknown detector type: {name}")
        return self._detectors[name](**kwargs)
