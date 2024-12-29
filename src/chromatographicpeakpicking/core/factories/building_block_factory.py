# src/chromatographicpeakpicking/core/factories/building_block_factory.py
"""
Module: building_block_factory

This module defines the BuildingBlockFactory class, which provides a method for creating
BuildingBlock instances using the Factory Pattern.

Design Patterns:
    - Factory Pattern: Used to create objects without specifying the exact class of the object that
      will be created. It provides a way to encapsulate the instantiation logic and centralize object
      creation in a single location.

Rationale:
    - Encapsulation: The Factory Pattern encapsulates the instantiation logic, making it easier to manage
      and maintain.
    - Validation: Allows for centralized validation of object creation parameters, ensuring that all created
      objects are in a valid state.
    - Flexibility: Provides flexibility in creating different types of objects, allowing for changes in the
      creation process without affecting the client code.
    - Decoupling: Decouples the client code from the specific classes being instantiated, promoting the
      Open/Closed Principle by enabling the addition of new types of objects without modifying existing code.
"""
from typing import Dict, Any, Optional
from ..prototypes.building_block import BuildingBlock

class BuildingBlockFactory:
    """
    Factory class for creating BuildingBlock instances.

    This class encapsulates the logic for creating BuildingBlock instances, ensuring that all
    necessary validations are performed during the creation process.
    """

    @staticmethod
    def create(name: str, smiles: str, properties: Optional[Dict[str, Any]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> BuildingBlock:
        """
        Create a new BuildingBlock instance.

        Args:
            name (str): The name of the building block.
            smiles (str): The SMILES string of the building block.
            properties (Optional[Dict[str, Any]]): Additional properties of the building block.
            metadata (Optional[Dict[str, Any]]): Metadata associated with the building block.

        Raises:
            ValueError: If the building block name is empty.
            ValueError: If the building block SMILES string is empty.

        Returns:
            BuildingBlock: A new BuildingBlock instance.
        """
        if not name:
            raise ValueError("Building block name cannot be empty")
        if not smiles:
            raise ValueError("Building block SMILES string cannot be empty")
        return BuildingBlock(
            name=name,
            smiles=smiles,
            properties=properties or {},
            metadata=metadata or {}
        )
