# src/chromatographicpeakpicking/core/pipeline/result.py
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Dict, Any, List
from ..core.types.errors import ProcessingError

T = TypeVar('T')

@dataclass(frozen=True)
class StageResult(Generic[T]):
   """
   Immutable result from a pipeline stage execution.

   Attributes:
       output: The stage's output data
       metadata: Additional metadata about the execution
       errors: Processing errors that occurred
       warnings: Processing warnings that occurred
       execution_time: Time taken to execute in seconds
   """
   output: T
   metadata: Dict[str, Any]
   errors: List[ProcessingError]
   warnings: List[ProcessingError]
   execution_time: float

@dataclass(frozen=True)
class PipelineResult(Generic[T]):
   """
   Immutable result from full pipeline execution.

   Attributes:
       final_output: The pipeline's final output
       stage_results: Results from individual stages
       total_time: Total execution time in seconds
   """
   final_output: T
   stage_results: Dict[str, StageResult]
   total_time: float
