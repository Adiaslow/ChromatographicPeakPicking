# src/chromatographicpeakpicking/core/factories/building_block_factory.py
"""
Module: building_block_factory

This module defines the BuildingBlockFactory class, which is responsible for creating BuildingBlock
instances. The BuildingBlockFactory class follows the Factory Pattern and the Prototype Pattern to
allow for efficient creation and cloning of BuildingBlock instances with optional modifications.

Design Patterns:
    - Factory Pattern: Used to create objects without specifying the exact class of object that will
        be created.
    - Prototype Pattern: Used to create new objects by copying an existing BuildingBlock instance.
    - Singleton Pattern: Used to ensure that only one instance of the BuildingBlockCache is created.
Rationale:
    - Efficiency: Creating building blocks using a factory can streamline the process, especially
        when dealing with complex initialization logic.
    - Simplicity: The Factory Pattern simplifies object creation by encapsulating the creation logic.
    - Flexibility: The Prototype Pattern provides flexibility in creating new objects based on an
        existing prototype with slight variations, reducing the need for multiple constructors or
        factory methods.
"""

from typing import Dict, Any
from ..prototypes.building_block import BuildingBlock
from ...implementations.singletons.building_block_cache import BuildingBlockCache

class BuildingBlockFactory:
    """
    Responsible for creating BuildingBlock instances.

    This class encapsulates the logic for creating new BuildingBlock instances,
    including the creation of building blocks with specific properties and metadata.

    Attributes:
        cache (BuildingBlockCache): The singleton cache for storing and retrieving building block prototypes.
    """

    def __init__(self):
        """Initialize the BuildingBlockFactory with a singleton cache."""
        self.cache = BuildingBlockCache()

    def register_prototype(self, name: str, building_block: BuildingBlock) -> None:
            """
            Register a prototype building block in the cache.

            Args:
                name (str): The name to register the prototype under.
                building_block (BuildingBlock): The BuildingBlock instance to register as a prototype.

            Raises:
                AttributeError: If self.cache is None
            """
            if self.cache is None:
                raise AttributeError("Cache has not been initialized")
            self.cache.set(name, building_block)

    def create_building_block(self, prototype_name: str, **kwargs: Any) -> BuildingBlock:
            """
            Create a new BuildingBlock instance based on a registered prototype, allowing for optional overrides.

            Args:
                prototype_name (str): The name of the prototype to use as the basis for the new instance.
                kwargs (Any): Attributes to override in the new instance.

            Returns:
                BuildingBlock: A new BuildingBlock instance based on the prototype with the specified overrides.

            Raises:
                ValueError: If the prototype_name is not registered.
                AttributeError: If self.cache is None.
            """
            if self.cache is None:
                raise AttributeError("Cache has not been initialized")
            prototype = self.cache.get(prototype_name)
            if prototype is None:
                raise ValueError(f"Prototype '{prototype_name}' is not registered.")
            return prototype.clone(**kwargs)

    def list_prototypes(self) -> Dict[str, BuildingBlock]:
        """
        List all registered prototype building blocks.

        Returns:
            Dict[str, BuildingBlock]: A dictionary of registered prototype building blocks.
        """
        return self.cache.cache

    def unregister_prototype(self, name: str) -> None:
        """
        Unregister a prototype building block from the cache.

        Args:
            name (str): The name of the prototype to unregister.

        Raises:
            ValueError: If the prototype_name is not registered.
        """
        if self.cache.get(name) is None:
            raise ValueError(f"Prototype '{name}' is not registered.")
        self.cache.remove(name)
