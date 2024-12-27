# src/chromatographicpeakpicking/core/factories/pipeline_factory.py
from dataclasses import dataclass, field
from typing import Dict, Type, Optional
from ..protocols.correctable import BaselineCorrector
from ..protocols.detectable import PeakDetector
from ..protocols.selectable import PeakSelector

@dataclass
class PipelineFactory:
    """Factory for creating analysis pipelines."""

    _correctors: Dict[str, Type[BaselineCorrector]] = field(default_factory=dict)
    _detectors: Dict[str, Type[PeakDetector]] = field(default_factory=dict)
    _selectors: Dict[str, Type[PeakSelector]] = field(default_factory=dict)

    def register_corrector(self, name: str, corrector: Type[BaselineCorrector]) -> None:
        """Register a baseline corrector type."""
        self._correctors[name] = corrector

    def register_detector(self, name: str, detector: Type[PeakDetector]) -> None:
        """Register a peak detector type."""
        self._detectors[name] = detector

    def register_selector(self, name: str, selector: Type[PeakSelector]) -> None:
        """Register a peak selector type."""
        self._selectors[name] = selector

    def create_pipeline(self,
                       corrector: Optional[str] = None,
                       detector: Optional[str] = None,
                       selector: Optional[str] = None,
                       **kwargs) -> 'AnalysisPipeline':
        """Create a complete analysis pipeline."""
        components = {}

        if corrector:
            if corrector not in self._correctors:
                raise KeyError(f"Unknown corrector type: {corrector}")
            components['corrector'] = self._correctors[corrector](**kwargs)

        if detector:
            if detector not in self._detectors:
                raise KeyError(f"Unknown detector type: {detector}")
            components['detector'] = self._detectors[detector](**kwargs)

        if selector:
            if selector not in self._selectors:
                raise KeyError(f"Unknown selector type: {selector}")
            components['selector'] = self._selectors[selector](**kwargs)

        return AnalysisPipeline(**components)
