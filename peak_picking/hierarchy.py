from collections import defaultdict
from typing import Dict, Generic, List, Optional, Set, TypeVar, Tuple
from itertools import combinations

from .building_block import BuildingBlock

T = TypeVar('T')  # Type of elements in the sequence
N = TypeVar('N')  # Type of null element
V = TypeVar('V')  # Type of value (typically float for elution times)

class Hierarchy(Generic[T, N, V]):
    """
    Represents a hierarchical structure of sequences where elements can be replaced by a null value,
    with optional values (e.g., elution times) associated with complete sequences.
    """

    def __init__(self, null_element: BuildingBlock):
        """
        Initialize the hierarchy with a specified null element

        Args:
            null_element: BuildingBlock that represents a null/empty position
        """
        self.null_element = null_element
        self.levels: Dict[int, Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
        self.descendants: Dict[Tuple[BuildingBlock, ...], Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
        self.ancestors: Dict[Tuple[BuildingBlock, ...], Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
        self.sequence_values: Dict[Tuple[BuildingBlock, ...], V] = {}

    def count_non_null(self, sequence: Tuple[BuildingBlock, ...]) -> int:
        """Returns the number of non-null elements in the sequence"""
        return sum(1 for elem in sequence if elem != self.null_element)

    def get_direct_descendants(self, sequence: Tuple[BuildingBlock, ...]) -> Set[Tuple[BuildingBlock, ...]]:
        """
        Generate all direct descendants of a sequence by replacing one non-null element with null
        """
        descendants = set()
        for i, elem in enumerate(sequence):
            if elem != self.null_element:
                descendant = sequence[:i] + (self.null_element,) + sequence[i+1:]
                descendants.add(descendant)
        return descendants

    def generate_descendants_with_k_elements(self, sequence: Tuple[BuildingBlock, ...], k: int) -> Set[Tuple[BuildingBlock, ...]]:
        """
        Generate all sequences with exactly k non-null elements that preserve the relative order
        of elements from the original sequence.
        """
        result = set()

        # Get non-null elements in their original order
        non_null_elements = [elem for elem in sequence if elem != self.null_element]
        length = len(sequence)

        # If k is greater than available non-null elements, return empty set
        if k > len(non_null_elements):
            return result

        # Select k elements while preserving order
        for selected_indices in combinations(range(len(non_null_elements)), k):
            selected_elements = [non_null_elements[i] for i in selected_indices]

            # Generate all possible positions for these k elements while maintaining their order
            def place_elements(curr_pos: int, elem_idx: int, curr_sequence: List[BuildingBlock]) -> None:
                if elem_idx == len(selected_elements):
                    result.add(tuple(curr_sequence))
                    return

                # Try placing the current element at each remaining valid position
                element = selected_elements[elem_idx]
                min_pos = curr_pos
                max_pos = length - (len(selected_elements) - elem_idx)

                for pos in range(min_pos, max_pos + 1):
                    new_sequence = curr_sequence.copy()
                    new_sequence[pos] = element
                    place_elements(pos + 1, elem_idx + 1, new_sequence)

            # Initialize sequence with null elements
            initial_sequence = [self.null_element] * length
            place_elements(0, 0, initial_sequence)

        return result

    def generate_all_descendants(self, sequence: Tuple[BuildingBlock, ...]) -> List[Tuple[BuildingBlock, ...]]:
        """Generate all possible descendants of a sequence that preserve relative order."""
        sequences = []
        original_length = len(sequence)
        non_null_count = self.count_non_null(sequence)

        for k in range(non_null_count + 1):
            sequences_with_k = self.generate_descendants_with_k_elements(sequence, k)
            sequences.extend(sequences_with_k)

        return sequences

    def add_sequence(self, sequence: Tuple[BuildingBlock, ...]) -> None:
        """Add a sequence to the hierarchy and compute its relationships"""
        level = self.count_non_null(sequence)
        self.levels[level].add(sequence)

        # Generate and store direct descendants
        direct_desc = self.get_direct_descendants(sequence)
        self.descendants[sequence].update(direct_desc)

        # Update ancestor relationships
        for desc in direct_desc:
            self.ancestors[desc].add(sequence)

    def add_sequences(self, sequences: List[Tuple[BuildingBlock, ...]]) -> None:
        """Add multiple sequences to the hierarchy"""
        for sequence in sequences:
            self.add_sequence(sequence)

    def get_sequences_by_level(self, level: int) -> Set[Tuple[BuildingBlock, ...]]:
        """Get all sequences with a specific number of non-null elements"""
        return self.levels[level]

    def get_level(self, sequence: Tuple[BuildingBlock, ...]) -> int:
        """Get the level (number of non-null elements) of a sequence"""
        return self.count_non_null(sequence)

    def get_ancestors(self, sequence: Tuple[BuildingBlock, ...]) -> Set[Tuple[BuildingBlock, ...]]:
        """Get all sequences that can have elements replaced to get this sequence"""
        return self.ancestors[sequence]

    def get_descendants(self, sequence: Tuple[BuildingBlock, ...]) -> Set[Tuple[BuildingBlock, ...]]:
        """Get direct descendants of a sequence"""
        return self.descendants[sequence]

    def set_sequence_value(self, sequence: Tuple[BuildingBlock, ...], value: V) -> None:
        """Set a value for a specific sequence"""
        self.sequence_values[sequence] = value

    def set_sequence_values(self, values: Dict[Tuple[BuildingBlock, ...], V]) -> None:
        """Set values for multiple sequences at once"""
        self.sequence_values.update(values)

    def get_sequence_value(self, sequence: Tuple[BuildingBlock, ...]) -> Optional[V]:
        """Get the value associated with a sequence"""
        return self.sequence_values.get(sequence)
