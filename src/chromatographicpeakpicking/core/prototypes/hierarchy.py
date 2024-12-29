# src/chromatographicpeakpicking/core/prototypes/hierarchy.py
"""
Module: hierarchy

This module defines the Hierarchy class for managing hierarchical structures of null truncations
in null-encoded peptide libraries. The Hierarchy class follows the Prototype Pattern to allow for
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

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional
from itertools import combinations
import copy
from ..types.config import GlobalConfig
from .building_block import BuildingBlock
from .peptide import Peptide

@dataclass
class Hierarchy:
    """
    Represents the hierarchical relational structure of null truncations in null-encoded peptide
    libraries.

    Attributes:
        global_config (GlobalConfig): Global configuration settings.
        levels (Dict[int, Set[Peptide]]): Dictionary mapping level (number of non-null building blocks) to sets of peptides.
        descendants (Dict[Peptide, Set[Peptide]]): Dictionary mapping peptides to their direct descendants.
        ancestors (Dict[Peptide, Set[Peptide]]): Dictionary mapping peptides to their direct ancestors.
    """
    global_config: GlobalConfig = field(default_factory=GlobalConfig)
    levels: Dict[int, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    descendants: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    ancestors: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))

    def count_non_null_blocks(self, peptide: Peptide) -> int:
        """
        Returns the number of non-null building blocks in the peptide.

        Args:
            peptide (Peptide): The peptide to count non-null building blocks in.

        Returns:
            int: The number of non-null building blocks.
        """
        null_building_block = self.global_config.null_building_block
        return sum(block != null_building_block for block in peptide.sequence)

    def get_direct_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """
        Generate all direct descendants of a peptide by replacing one non-null building block with null.

        Args:
            peptide (Peptide): The peptide to generate descendants for.

        Returns:
            Set[Peptide]: A set of direct descendant peptides.
        """
        null_building_block = self.global_config.null_building_block
        return {
            Peptide(sequence=peptide.sequence[:i] + [null_building_block] + peptide.sequence[i + 1:])
            for i, block in enumerate(peptide.sequence)
            if block != null_building_block
        }

    def generate_descendants_with_k_blocks(self, peptide: Peptide, k: int) -> Set[Peptide]:
        """
        Generate all peptides with exactly k non-null building blocks that preserve the relative order
        of building blocks.

        Args:
            peptide (Peptide): The peptide to generate descendants for.
            k (int): The number of non-null building blocks in the generated peptides.

        Returns:
            Set[Peptide]: A set of peptides with exactly k non-null building blocks.
        """
        result = set()
        null_building_block = self.global_config.null_building_block
        non_null_blocks = [block for block in peptide.sequence if block != null_building_block]
        length = len(peptide.sequence)

        if k > len(non_null_blocks):
            return result

        def place_blocks(curr_pos: int, block_idx: int, curr_peptide: List[BuildingBlock]) -> None:
            if block_idx == len(selected_blocks):
                result.add(Peptide(sequence=curr_peptide))
                return

            block = selected_blocks[block_idx]
            min_pos = curr_pos
            max_pos = length - (len(selected_blocks) - block_idx)

            for pos in range(min_pos, max_pos + 1):
                new_peptide = curr_peptide.copy()
                new_peptide[pos] = block
                place_blocks(pos + 1, block_idx + 1, new_peptide)

        for selected_indices in combinations(range(len(non_null_blocks)), k):
            selected_blocks = [non_null_blocks[i] for i in selected_indices]
            initial_peptide = [null_building_block] * length
            place_blocks(0, 0, initial_peptide)

        return result

    def generate_all_descendants(self, peptide: Peptide) -> List[Peptide]:
        """
        Generate all possible descendants of a peptide that preserve relative order.

        Args:
            peptide (Peptide): The peptide to generate descendants for.

        Returns:
            List[Peptide]: A list of all possible descendant peptides.
        """
        peptides = []
        non_null_count = self.count_non_null_blocks(peptide)

        for k in range(non_null_count + 1):
            peptides_with_k = self.generate_descendants_with_k_blocks(peptide, k)
            peptides.extend(peptides_with_k)

        return peptides

    def add_peptide(self, peptide: Peptide) -> None:
        """
        Add a peptide to the hierarchy and compute its relationships.

        Args:
            peptide (Peptide): The peptide to add.
        """
        level = self.count_non_null_blocks(peptide)
        self.levels[level].add(peptide)
        direct_desc = self.get_direct_descendants(peptide)
        self.descendants[peptide].update(direct_desc)

        for desc in direct_desc:
            self.ancestors[desc].add(peptide)

    def add_peptides(self, peptides: List[Peptide]) -> None:
        """
        Add multiple peptides to the hierarchy.

        Args:
            peptides (List[Peptide]): The list of peptides to add.
        """
        for peptide in peptides:
            self.add_peptide(peptide)

    def get_peptides_by_level(self, level: int) -> Set[Peptide]:
        """
        Get all peptides with a specific number of non-null building blocks.

        Args:
            level (int): The level to get peptides for.

        Returns:
            Set[Peptide]: A set of peptides at the specified level.
        """
        return self.levels[level]

    def get_level(self, peptide: Peptide) -> int:
        """
        Get the level (number of non-null building blocks) of a peptide.

        Args:
            peptide (Peptide): The peptide to get the level for.

        Returns:
            int: The level of the peptide.
        """
        return self.count_non_null_blocks(peptide)

    def get_ancestors(self, peptide: Peptide) -> Set[Peptide]:
        """
        Get all peptides that can have building blocks replaced to get this peptide.

        Args:
            peptide (Peptide): The peptide to get ancestors for.

        Returns:
            Set[Peptide]: A set of ancestor peptides.
        """
        return self.ancestors[peptide]

    def get_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """
        Get direct descendants of a peptide.

        Args:
            peptide (Peptide): The peptide to get descendants for.

        Returns:
            Set[Peptide]: A set of direct descendant peptides.
        """
        return self.descendants[peptide]

    def clone(self, **kwargs: Any) -> 'Hierarchy':
        """
        Clone the current hierarchy, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            Hierarchy: A new Hierarchy instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance

    def with_peptides(self, peptides: List[Peptide]) -> 'Hierarchy':
        """
        Create a new hierarchy instance with updated peptides.

        Args:
            peptides (List[Peptide]): The list of peptides to add.

        Returns:
            Hierarchy: A new Hierarchy instance with updated peptides.
        """
        new_instance = self.clone()
        new_instance.add_peptides(peptides)
        return new_instance
