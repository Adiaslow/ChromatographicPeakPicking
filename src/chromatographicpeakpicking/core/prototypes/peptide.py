# src/chromatographicpeakpicking/core/prototypes/peptide.py
"""
Module: peptide

This module defines the Peptide class, which represents a peptide sequence with its associated
building blocks and chromatograms. The Peptide class follows the Prototype Pattern to allow for
efficient cloning of instances with optional modifications.

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
from typing import List, Dict, Any, Optional
from uuid import uuid4
import copy
from .building_block import BuildingBlock
from .chromatogram import Chromatogram

@dataclass(frozen=True)
class Peptide:
    """
    Represents a peptide sequence with its associated building blocks and chromatograms.

    Attributes:
        sequence (List[BuildingBlock]): The sequence of building blocks (amino acids).
        chromatograms (List[Chromatogram]): The list of associated chromatograms.
        properties (Dict[str, Any]): Additional properties of the peptide.
        metadata (Dict[str, Any]): Additional metadata about the peptide.
        id (str): A unique identifier for the peptide.
    """

    sequence: List[BuildingBlock] = field(default_factory=list)
    chromatograms: List[Chromatogram] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate peptide data."""
        if not self.sequence:
            raise ValueError("Peptide must have at least one building block")
        if 'retention_time' in self.properties and self.properties['retention_time'] < 0:
            raise ValueError("Retention time must be non-negative")

    @property
    def length(self) -> int:
        """Get peptide length."""
        return len(self.sequence)

    def get_building_block_at_position(self, position: int) -> BuildingBlock:
        """Get building block at specific position."""
        if not 0 <= position < len(self.sequence):
            raise IndexError("Position out of range")
        return self.sequence[position]

    def clone(self, **kwargs: Any) -> 'Peptide':
        """
        Clone the current peptide, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            Peptide: A new Peptide instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        # Set a new unique ID unless explicitly provided in kwargs
        new_instance_id = kwargs.get('id', str(uuid4()))
        object.__setattr__(new_instance, 'id', new_instance_id)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance

    def with_properties(self, **kwargs: Any) -> 'Peptide':
        """Create new peptide with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs) -> 'Peptide':
        """Create new peptide with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def with_chromatograms(self, chromatograms: List[Chromatogram]) -> 'Peptide':
        """Create a new peptide instance with updated chromatograms."""
        return self.clone(chromatograms=chromatograms)

    def get_sequence_string(self, separator: str = "-", reverse: bool = False) -> str:
        """
        Get string representation of peptide sequence.

        Args:
            separator (str): The separator to use between building blocks in the sequence.
            reverse (bool): Whether to describe the sequence from C-terminus to N-terminus.

        Returns:
            str: The string representation of the peptide sequence.
        """
        sequence = self.sequence[::-1] if reverse else self.sequence
        return separator.join(block.name for block in sequence)

    def __eq__(self, other: object) -> bool:
        """Check if two peptides are equal."""
        if not isinstance(other, Peptide):
            return NotImplemented
        return self.sequence == other.sequence

    def __hash__(self) -> int:
        return hash(tuple(self.sequence))

    def __str__(self) -> str:
        """Get string representation of peptide."""
        rt_str = f", RT={self.properties.get('retention_time', 'N/A'):.2f}" if 'retention_time' in self.properties else ""
        return f"Peptide({self.get_sequence_string()}{rt_str})"
