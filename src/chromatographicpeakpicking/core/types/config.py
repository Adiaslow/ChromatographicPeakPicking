# src/chromatographicpeakpicking/core/types/config.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum

class ConfigValidation(Enum):
    """Configuration validation levels."""
    STRICT = "strict"       # Fail on any validation error
    PERMISSIVE = "permissive"  # Allow unknown fields
    SILENT = "silent"       # Skip validation

@dataclass(frozen=True)
class ConfigMetadata:
    """
    Metadata about a configurable component.

    Attributes:
        name: Unique identifier for this configuration
        version: Version of the configuration schema
        description: Human-readable description
        defaults: Default values for configuration
        schema: JSON schema for validation
        validation_level: How strictly to validate
    """
    name: str
    version: str
    description: str
    defaults: Dict[str, Any]
    schema: Dict[str, Any]
    validation_level: ConfigValidation = ConfigValidation.STRICT

@dataclass
class BaseConfig:
    """
    Base configuration container.

    Attributes:
        metadata: Configuration metadata
        parameters: Configuration parameters
        _validated: Whether config has been validated
    """
    metadata: ConfigMetadata
    parameters: Dict[str, Any] = field(default_factory=dict)
    _validated: bool = field(default=False, init=False)
