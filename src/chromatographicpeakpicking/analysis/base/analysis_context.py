# src/chromatographicpeakpicking/analysis/base/analysis_context.py
from typing import Dict, Any, Optional
from ..protocols.analyzer import Analyzer, AnalysisResult
from ...infrastructure.logging.analysis_logger import AnalysisLogger

class AnalysisContext:
    """Context for managing analysis operations."""

    def __init__(self, logger: Optional[AnalysisLogger] = None):
        self._logger = logger
        self._analyzers: Dict[str, Analyzer] = {}

    def register_analyzer(self, name: str, analyzer: Analyzer) -> None:
        """Register an analyzer with the context."""
        self._analyzers[name] = analyzer
        if self._logger:
            self._logger.log_analysis_step(f"Registered analyzer: {name}")

    async def run_analysis(self, name: str, data: Any) -> AnalysisResult:
        """Run analysis using a registered analyzer."""
        if name not in self._analyzers:
            raise ValueError(f"No analyzer registered with name: {name}")

        analyzer = self._analyzers[name]

        if self._logger:
            self._logger.log_analysis_start(f"Starting analysis: {name}")

        if not await analyzer.validate(data):
            raise ValueError("Input data validation failed")

        result = await analyzer.analyze(data)

        if self._logger:
            self._logger.log_analysis_end(f"Completed analysis: {name}")

        return result
