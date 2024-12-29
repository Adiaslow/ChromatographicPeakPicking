# src/chromatographicpeakpicking/pipeline/analysis_pipeline.py
"""
This module defines the AnalysisPipeline class, which is used to represent and execute a
chromatographic analysis pipeline.
"""

from typing import Optional, Union, List
from ..core.protocols.correctable import Correctable
from ..core.protocols.detectable import Detectable
from ..core.protocols.selectable import Selectable

class AnalysisPipeline:
    """Represents a complete analysis pipeline."""

    def __init__(self,
                 corrector: Optional[Union[Correctable, List[Correctable]]] = None,
                 detector: Optional[Union[Detectable, List[Detectable]]] = None,
                 selector: Optional[Union[Selectable, List[Selectable]]] = None):
        # Ensure components are stored as lists
        if corrector is None:
            self.correctors = []
        elif isinstance(corrector, list):
            self.correctors = corrector
        else:
            self.correctors = [corrector]

        if detector is None:
            self.detectors = []
        elif isinstance(detector, list):
            self.detectors = detector
        else:
            self.detectors = [detector]

        if selector is None:
            self.selectors = []
        elif isinstance(selector, list):
            self.selectors = selector
        else:
            self.selectors = [selector]

    def run(self, data):
        """Run the analysis pipeline on the provided data."""
        # Apply each corrector in order
        for corrector in self.correctors:
            data = corrector.correct(data)

        # Apply each detector in order
        peaks = []
        for detector in self.detectors:
            peaks = detector.detect(data)

        # Apply each selector in order
        for selector in self.selectors:
            peaks = selector.select(peaks)

        return peaks
