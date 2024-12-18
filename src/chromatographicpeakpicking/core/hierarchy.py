# External imports
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Generic, List, Optional, Set, TypeVar, Tuple
from itertools import combinations
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

# Internal imports
from configs.global_config import GlobalConfig
from core.building_block import BuildingBlock

T = TypeVar('T')  # Type of elements in the sequence
N = TypeVar('N')  # Type of null element
V = TypeVar('V')  # Type of value (typically float for elution times)

@dataclass
class Hierarchy(
    Generic[T, N, V]
):
    """Represents a hierarchical structure of sequences where elements can be replaced by a null value,
        with optional values (e.g., elution times) associated with complete sequences.

    Attributes:
        null_element: BuildingBlock that represents a null/empty position
    """
    global_config: GlobalConfig = field(default_factory=GlobalConfig)

    null_element: BuildingBlock = global_config.null_building_block
    levels: Dict[int, Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
    descendants: Dict[Tuple[BuildingBlock, ...], Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
    ancestors: Dict[Tuple[BuildingBlock, ...], Set[Tuple[BuildingBlock, ...]]] = defaultdict(set)
    sequence_values: Dict[Tuple[BuildingBlock, ...], V] = {}

    def count_non_null(self, sequence: Tuple[BuildingBlock, ...]) -> int:
        """Returns the number of non-null elements in the sequence"""
        return sum(bool(elem != self.null_element)
               for elem in sequence)

    def get_direct_descendants(self, sequence: Tuple[BuildingBlock, ...]) -> Set[Tuple[BuildingBlock, ...]]:
        """
        Generate all direct descendants of a sequence by replacing one non-null element with null
        """
        return {
            sequence[:i] + (self.null_element,) + sequence[i + 1 :]
            for i, elem in enumerate(sequence)
            if elem != self.null_element
        }

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
        # original_length = len(sequence)
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

    def visualize_hierarchy(self, figsize=(12, 8), node_size=2000,
                           with_values: bool = False,
                           save_path: Optional[str] = None,
                           color_scheme: Optional[Dict[int, str]] = None) -> None:
        """
        Visualize a Hierarchy object using NetworkX and Matplotlib.

        Args:
            hierarchy: Hierarchy object to visualize
            figsize: Tuple of (width, height) for the figure
            node_size: Size of nodes in the visualization
            with_values: Whether to display sequence values in nodes
            save_path: Optional path to save the visualization
            color_scheme: Optional dictionary mapping levels to colors
        """
        # Create directed graph
        G = nx.DiGraph()

        # Get all sequences grouped by level
        max_level = max(self.levels.keys())

        # Default color scheme if none provided
        if color_scheme is None:
            colors = list(mcolors.TABLEAU_COLORS.values())
            color_scheme = {
                level: colors[i % len(colors)]
                for i, level in enumerate(range(max_level + 1))
            }

        # Calculate positions for nodes
        pos = {}
        for level in range(max_level + 1):
            sequences = self.get_sequences_by_level(level)
            if not sequences:
                continue

            # Calculate y-coordinate based on level
            y = (max_level - level) / max_level

            # Position nodes horizontally
            for i, seq in enumerate(sorted(sequences)):
                x = (i + 1) / (len(sequences) + 1)
                pos[seq] = (x, y)

                # Create node label
                if with_values:
                    value = self.get_sequence_value(seq)
                    label = f"{'.'.join(str(x) for x in seq)}\n{value:.2f}" if value is not None else '.'.join(str(x) for x in seq)
                else:
                    label = '.'.join(str(x) for x in seq)

                # Add node with attributes
                G.add_node(seq,
                          label=label,
                          level=level,
                          color=color_scheme[level])

        # Add edges
        for seq in G.nodes():
            descendants = self.get_descendants(seq)
            for desc in descendants:
                G.add_edge(seq, desc)

        # Create visualization
        plt.figure(figsize=figsize)

        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}

        nx.draw(G, pos,
                with_labels=True,
                labels=labels,
                node_color=node_colors,
                node_size=node_size,
                arrowsize=20,
                font_size=10,
                font_weight='bold',
                edge_color='gray',
                arrows=True)

        # Add legend for levels
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=color,
                                     markersize=10,
                                     label=f'Level {level}')
                          for level, color in color_scheme.items()]
        plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))

        plt.title("Hierarchy Visualization")

        # Save or show
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        else:
            plt.show()

        plt.close()
