# src/chromatographicpeakpicking/core/domain/peptide.py
"""
This module defines the Peptide class, which represents a peptide sequence
with its associated building blocks and properties.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import uuid4
from .building_block import BuildingBlock

@dataclass(frozen=True)
class Peptide:
    """
    Represents a peptide sequence with its associated building blocks and properties.

    Attributes:
        sequence (List[BuildingBlock]): The sequence of building blocks (amino acids).
        retention_time (Optional[float]): The retention time of the peptide.
        peak_area (Optional[float]): The peak area of the peptide.
        peak_height (Optional[float]): The peak height of the peptide.
        metadata (Dict[str, Any]): Additional metadata about the peptide.
        id (str): A unique identifier for the peptide.
    """

    sequence: List[BuildingBlock]
    retention_time: Optional[float] = None
    peak_area: Optional[float] = None
    peak_height: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate peptide data."""
        if not self.sequence:
            raise ValueError("Peptide must have at least one building block")
        if self.retention_time is not None and self.retention_time < 0:
            raise ValueError("Retention time must be non-negative")

    @property
    def length(self) -> int:
        """Get peptide length."""
        return len(self.sequence)

    @property
    def mass(self) -> float:
        """Calculate total peptide mass."""
        return sum(block.mass for block in self.sequence)

    def get_building_block_at_position(self, position: int) -> BuildingBlock:
        """Get building block at specific position."""
        if not 0 <= position < len(self.sequence):
            raise IndexError("Position out of range")
        return self.sequence[position]

    def with_retention_time(self, retention_time: float) -> 'Peptide':
        """Create new peptide with updated retention time."""
        if retention_time < 0:
            raise ValueError("Retention time must be non-negative")
        return Peptide(
            id=self.id,
            sequence=self.sequence,
            retention_time=retention_time,
            peak_area=self.peak_area,
            peak_height=self.peak_height,
            metadata=self.metadata
        )

    def with_peak_metrics(
        self,
        area: Optional[float] = None,
        height: Optional[float] = None
    ) -> 'Peptide':
        """Create new peptide with updated peak metrics."""
        return Peptide(
            id=self.id,
            sequence=self.sequence,
            retention_time=self.retention_time,
            peak_area=area if area is not None else self.peak_area,
            peak_height=height if height is not None else self.peak_height,
            metadata=self.metadata
        )

    def with_metadata(self, **kwargs) -> 'Peptide':
        """Create new peptide with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return Peptide(
            id=self.id,
            sequence=self.sequence,
            retention_time=self.retention_time,
            peak_area=self.peak_area,
            peak_height=self.peak_height,
            metadata=new_metadata
        )

    def get_sequence_string(self, separator: str = "-") -> str:
        """Get string representation of peptide sequence."""
        return separator.join(block.name for block in self.sequence)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Peptide):
            return NotImplemented
        return self.sequence == other.sequence

    def __hash__(self) -> int:
        return hash(tuple(self.sequence))

    def __str__(self) -> str:
        rt_str = f", RT={self.retention_time:.2f}" if self.retention_time else ""
        return f"Peptide({self.get_sequence_string()}{rt_str})"
