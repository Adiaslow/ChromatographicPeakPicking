# src/chromatographicpeakpicking/core/domain/building_block.py
"""
Module: building_block

This module defines the BuildingBlock class, which represents a peptide building block such as an
amino acid, non-natural amino acid, peptoid, or polypeptide. The BuildingBlock class follows the
Prototype Pattern to allow for efficient cloning of instances with optional modifications.

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
from typing import Dict, Any, Optional
from uuid import uuid4
import copy

@dataclass(frozen=True)
class BuildingBlock:
    """
    Represents a peptide building block.

    This class encapsulates all information about a peptide building block,
    including its name, unique identifier, properties, metadata.

    Attributes:
        name (str): The name of the building block.
        id (str): A unique identifier for the building block.
        smiles (str): The SMILES string of the building block.
        properties (Dict[str, Any]): Additional properties of the building block.
        metadata (Dict[str, Any]): Metadata associated with the building block.
    """

    name: str = field(default="")
    id: str = field(default_factory=lambda: str(uuid4()))
    smiles: str = field(default="")
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validate building block data after initialization.

        Raises:
            ValueError: If the building block name is empty.
            ValueError: If the building block ID is empty.
        """
        if self.name == "":
            raise ValueError("Building block name cannot be empty")
        if self.id == "":
            raise ValueError("Building block ID cannot be empty")

    def clone(self, **kwargs: Any) -> 'BuildingBlock':
        """
        Clone the current building block, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            BuildingBlock: A new BuildingBlock instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        # Set a new unique ID unless explicitly provided in kwargs
        new_instance_id = kwargs.get('id', str(uuid4()))
        object.__setattr__(new_instance, 'id', new_instance_id)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance
