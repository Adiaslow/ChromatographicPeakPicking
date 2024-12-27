# src/chromatographicpeakpicking/core/domain/building_block.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import uuid4

@dataclass(frozen=True)
class BuildingBlock:
    """
    Represents a peptide building block (amino acid or modified amino acid).
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str
    mass: float
    formula: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

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
            metadata=new_metadata
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuildingBlock):
            return NotImplemented
        return self.name == other.name and self.mass == other.mass

    def __hash__(self) -> int:
        return hash((self.name, self.mass))
