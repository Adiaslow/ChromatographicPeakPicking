# src/chromatographicpeakpicking/core/types/config.py
"""
This module defines configuration-related classes and enums for managing configurable components.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum

from ..prototypes.building_block import BuildingBlock

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

@dataclass
class GlobalConfig:
    """Global configuration settings.

    Attributes:
        debug: Enable debug mode
    """
    debug: bool = field(default=False)
    null_building_block: BuildingBlock = BuildingBlock(
        name="NULL",
        mass=0.0,
        formula="",
        smiles="",
        metadata={"is_null": True}
    )
    def __post_init__(self):
        # Initialize any other config settings here if needed
        pass
