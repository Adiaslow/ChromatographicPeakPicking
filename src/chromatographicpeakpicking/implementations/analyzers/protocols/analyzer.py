# src/chromatographicpeakpicking/analysis/protocols/analyzer.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, Any
from dataclasses import dataclass

Input = TypeVar('Input')
Output = TypeVar('Output')

@dataclass
class AnalysisResult(Generic[Output]):
    """Base class for analysis results."""
    result: Output
    metadata: Dict[str, Any]
    execution_time: float

class Analyzer(ABC, Generic[Input, Output]):
    """Base protocol for all analyzers."""

    @abstractmethod
    async def analyze(self, data: Input) -> AnalysisResult[Output]:
        """Analyze input data and return results."""
        pass

    @abstractmethod
    async def validate(self, data: Input) -> bool:
        """Validate input data before analysis."""
        pass
