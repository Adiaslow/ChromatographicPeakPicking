# src/peptide_chroma/pipeline/builders/pipeline_builder.py
from dataclasses import dataclass, field
from typing import Optional, List
from ...core.protocols.baseline_corrector import BaselineCorrector
from ...core.protocols.detectable import PeakDetector
from ...core.domain.chromatogram import Chromatogram
from ..observers.progress_observer import ProgressObserver

@dataclass
class AnalysisPipeline:
    """Configurable pipeline for chromatogram analysis."""

    baseline_corrector: Optional[BaselineCorrector] = None
    peak_detector: Optional[PeakDetector] = None
    observers: List[ProgressObserver] = field(default_factory=list)

    def process(self, chromatogram: Chromatogram) -> Chromatogram:
        """Process chromatogram through the pipeline."""
        current = chromatogram

        # Apply baseline correction if configured
        if self.baseline_corrector:
            self._notify_observers("baseline_correction", 0.0)
            self.baseline_corrector.validate(current)
            current = self.baseline_corrector.correct(current)
            self._notify_observers("baseline_correction", 1.0)

        # Apply peak detection if configured
        if self.peak_detector:
            self._notify_observers("peak_detection", 0.0)
            self.peak_detector.validate(current)
            peaks = self.peak_detector.detect(current)
            current = Chromatogram(
                time=current.time,
                intensity=current.intensity,
                metadata=current.metadata,
                peaks=peaks,
                baseline=current.baseline
            )
            self._notify_observers("peak_detection", 1.0)

        return current

    def _notify_observers(self, stage: str, progress: float) -> None:
        """Notify observers of pipeline progress."""
        for observer in self.observers:
            observer.update(stage, progress)
