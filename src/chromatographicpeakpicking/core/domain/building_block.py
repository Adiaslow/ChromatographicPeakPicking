# src/chromatographicpeakpicking/core/domain/building_block.py
"""
This module defines the BuildingBlock class, which represents a peptide building block such as an
amino acid or modified amino acid.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import uuid4

@dataclass(frozen=True)
class BuildingBlock:
    """
    Represents a peptide building block (amino acid or modified amino acid).

    This class encapsulates all information about a peptide building block,
    including its name, mass, chemical formula, metadata, and unique identifier.
    """

    name: str
    mass: float
    formula: Optional[str] = None
    smiles: Optional[str] = None
    properties: Optional[Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate building block data."""
        if self.mass <= 0:
            raise ValueError("Mass must be positive")

    def with_metadata(self, **kwargs) -> 'BuildingBlock':
        """Create new building block with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return BuildingBlock(
            id=self.id,
            name=self.name,
            mass=self.mass,
            formula=self.formula,
            smiles=self.smiles,
            properties=self.properties,
            metadata=new_metadata
        )

    def with_properties(self, **kwargs) -> 'BuildingBlock':
        """Create new building block with updated properties."""
        new_properties = self.properties.copy() if self.properties is not None else {}
        new_properties.update(kwargs)
        return BuildingBlock(
            id=self.id,
            name=self.name,
            mass=self.mass,
            formula=self.formula,
            smiles=self.smiles,
            properties=new_properties,
            metadata=self.metadata
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuildingBlock):
            return NotImplemented
        return self.name == other.name and self.mass == other.mass

    def __hash__(self) -> int:
        return hash((self.name, self.mass))
