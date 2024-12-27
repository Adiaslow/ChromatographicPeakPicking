# src/chromatographicpeakpicking/core/pipeline/stage.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from dataclasses import dataclass
from ..core.types.validation import ValidationResult
from ..core.types.errors import ProcessingError
from ..core.protocols.error_handler import ErrorHandler
from ..core.protocols.configurable import Configurable
from .result import StageResult

Input = TypeVar('Input')
Output = TypeVar('Output')
Config = TypeVar('Config')

class PipelineStage(ABC, Generic[Input, Output, Config]):
    """
    Abstract base class for pipeline stages.

    Each stage represents a discrete processing step that transforms
    input data into output data while maintaining error handling
    and validation.
    """

    def __init__(self,
                 name: str,
                 error_handler: ErrorHandler,
                 config: Config = None):
        self.name = name
        self._error_handler = error_handler
        self._config = config

    @abstractmethod
    def execute(self, input_data: Input) -> StageResult[Output]:
        """Execute stage processing on input data."""
        pass

    @abstractmethod
    def validate(self, input_data: Input) -> ValidationResult:
        """Validate that input data can be processed."""
        pass

    @property
    def error_handler(self) -> ErrorHandler:
        """Get stage's error handler."""
        return self._error_handler

    @property
    def config(self) -> Config:
        """Get stage's configuration."""
        return self._config
