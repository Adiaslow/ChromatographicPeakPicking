# src/chromatographicpeakpicking/core/types/__init__.py
"""
This module aggregates and re-exports key components related to configuration, errors, and
validation.
"""
from .config import (
    ConfigValidation,
    ConfigMetadata,
    BaseConfig
)
from .errors import (
    ErrorSeverity,
    ProcessingError
)
from .validation import ValidationResult

__all__ = [
    'ConfigValidation',
    'ConfigMetadata',
    'BaseConfig',
    'ErrorSeverity',
    'ProcessingError',
    'ValidationResult'
]
