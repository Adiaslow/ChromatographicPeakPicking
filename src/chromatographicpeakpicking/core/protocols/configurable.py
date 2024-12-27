# src/chromatographicpeakpicking/core/protocols/configurable.py
from typing import Protocol, TypeVar, Generic
from ..types.config import ConfigMetadata, BaseConfig
from ..types.validation import ValidationResult

T = TypeVar('T', bound=BaseConfig)

class Configurable(Protocol, Generic[T]):
    """Protocol for configurable components."""

    def configure(self, config: T) -> ValidationResult:
        """
        Configure the component.

        Args:
            config: Configuration data

        Returns:
            ValidationResult indicating if configuration was successful

        Raises:
            ConfigurationError: If configuration is invalid and validation is strict
        """
        ...

    def get_metadata(self) -> ConfigMetadata:
        """Get component's configuration metadata."""
        ...

    def validate_config(self, config: T) -> ValidationResult:
        """
        Validate configuration without applying it.

        Args:
            config: Configuration to validate

        Returns:
            ValidationResult with validation details
        """
        ...
