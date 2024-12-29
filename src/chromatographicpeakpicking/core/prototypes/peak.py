# src/chromatographicpeakpicking/core/domain/peak.py
"""
Module: peak

This module defines the Peak class, which represents a chromatographic peak
with its basic attributes. The Peak class follows the Prototype Pattern
to allow for efficient cloning of instances with optional modifications.

Design Patterns:
    - Prototype Pattern: Used to create new objects by copying an existing object (the prototype).

Rationale:
    - Efficiency: Cloning an existing object can be more efficient than creating a new one from
        scratch, especially when the object has already been initialized with a complex state.
    - Simplicity: The Prototype Pattern simplifies object creation by allowing for the reuse of
        existing objects with optional modifications.
    - Flexibility: Provides flexibility in creating new objects based on an existing prototype with
        slight variations, reducing the need for multiple constructors or factory methods.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4
import copy

@dataclass(frozen=True)
class Peak:
    """
    Represents a chromatographic peak with its basic attributes.

    Attributes:
        time (float): The time at which the peak occurs.
        index (int): The index of the peak in the dataset.
        intensity (float): The intensity of the peak.
        properties (Dict[str, Any]): Additional properties of the peak.
        metadata (Dict[str, Any]): Additional metadata about the peak.
        id (str): A unique identifier for the peak.
    """

    time: float
    index: int
    intensity: float
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def clone(self, **kwargs: Any) -> 'Peak':
        """
        Clone the current peak, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            Peak: A new Peak instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        # Set a new unique ID unless explicitly provided in kwargs
        new_instance_id = kwargs.get('id', str(uuid4()))
        object.__setattr__(new_instance, 'id', new_instance_id)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance

    def with_properties(self, **kwargs: Any) -> 'Peak':
        """Create new peak instance with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs) -> 'Peak':
        """Create new peak instance with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def __eq__(self, other: object) -> bool:
        """Compare peaks for equality based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time == other.time

    def __ne__(self, other: object) -> bool:
        """Compare peaks for inequality based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time != other.time

    def __lt__(self, other: object) -> bool:
        """Compare peaks for less than based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time < other.time

    def __gt__(self, other: object) -> bool:
        """Compare peaks for greater than based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time > other.time

    def __le__(self, other: object) -> bool:
        """Compare peaks for less than or equal based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time <= other.time

    def __ge__(self, other: object) -> bool:
        """Compare peaks for greater than or equal based on time."""
        if not isinstance(other, Peak):
            return NotImplemented
        return self.time >= other.time

    def __hash__(self) -> int:
        """Hash the peak based on its UUID id."""
        return hash(self.id)

    def __str__(self) -> str:
        """Return a string representation of the peak."""
        return f"Peak(time={self.time}, index={self.index}, intensity={self.intensity})"

    def __repr__(self) -> str:
        """Return a string representation of the peak."""
        return str(self)
