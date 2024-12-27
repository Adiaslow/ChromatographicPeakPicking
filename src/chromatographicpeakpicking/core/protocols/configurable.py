# src/chromatographicpeakpicking/core/protocols/configurable.py
"""
This module defines the Configurable protocol for components that can be configured.
"""

from typing import Protocol, TypeVar, Generic
from src.chromatographicpeakpicking.core.types.config import ConfigMetadata, BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

T_contra = TypeVar('T_contra', bound=BaseConfig, contravariant=True)

class Configurable(Protocol, Generic[T_contra]):
    """Protocol for configurable components."""

    def configure(self, config: T_contra) -> ValidationResult:
        """
        Configure the component.

        Args:
            config: Configuration data

        Returns:
            ValidationResult indicating if configuration was successful

        Raises:
            ConfigurationError: If configuration is invalid and validation is strict
        """
        raise NotImplementedError

    def get_metadata(self) -> ConfigMetadata:
        """Get component's configuration metadata."""
        raise NotImplementedError

    def validate_config(self, config: T_contra) -> ValidationResult:
        """
        Validate configuration without applying it.

        Args:
            config: Configuration to validate

        Returns:
            ValidationResult with validation details
        """
        raise NotImplementedError
