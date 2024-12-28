# src/chromatographicpeakpicking/core/domain/hierarchy.py
"""
This module defines the Hierarchy class for managing hierarchical structures of peptides.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Generic, List, Optional, Set, TypeVar
from itertools import combinations
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from ..types.config import GlobalConfig
from .building_block import BuildingBlock
from .peptide import Peptide

T = TypeVar('T')  # Type of elements in the sequence
V = TypeVar('V')  # Type of value (typically float for elution times)

@dataclass
class Hierarchy(Generic[T, V]):
    """Represents a hierarchical structure of peptides where elements can be replaced by a null
    value, with optional values (e.g., elution times) associated with complete peptides.

    Attributes:
        global_config: Global configuration settings.
        null_element: BuildingBlock that represents a null/empty position.
        levels: Dictionary mapping level (number of non-null elements) to sets of peptides.
        descendants: Dictionary mapping peptides to their direct descendants.
        ancestors: Dictionary mapping peptides to their direct ancestors.
        peptide_values: Dictionary mapping peptides to their associated values.
    """
    global_config: GlobalConfig = field(default_factory=GlobalConfig)
    null_element: BuildingBlock = field(init=False)
    levels: Dict[int, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    descendants: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    ancestors: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    peptide_values: Dict[Peptide, V] = field(default_factory=dict)

    def __post_init__(self):
        self.null_element = self.global_config.null_building_block

    def count_non_null(self, peptide: Peptide) -> int:
        """Returns the number of non-null elements in the peptide.

        Args:
            peptide (Peptide): The peptide to count non-null elements in.

        Returns:
            int: The number of non-null elements.
        """
        return sum(elem != self.null_element for elem in peptide)

    def get_direct_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """Generate all direct descendants of a peptide by replacing one non-null element with null.

        Args:
            peptide (Peptide): The peptide to generate descendants for.

        Returns:
            Set[Peptide]: A set of direct descendant peptides.
        """
        return {
            Peptide(peptide[:i] + [self.null_element] + peptide[i + 1:])
            for i, elem in enumerate(peptide)
            if elem != self.null_element
        }

    def generate_descendants_with_k_elements(self, peptide: Peptide, k: int) -> Set[Peptide]:
        """Generate all peptides with exactly k non-null elements that preserve the relative order
        of elements.

        Args:
            peptide (Peptide): The peptide to generate descendants for.
            k (int): The number of non-null elements in the generated peptides.

        Returns:
            Set[Peptide]: A set of peptides with exactly k non-null elements.
        """
        result = set()
        non_null_elements = [elem for elem in peptide if elem != self.null_element]
        length = len(peptide)

        if k > len(non_null_elements):
            return result

        def place_elements(curr_pos: int, elem_idx: int, curr_peptide: List[BuildingBlock]) -> None:
            if elem_idx == len(selected_elements):
                result.add(Peptide(curr_peptide))
                return

            element = selected_elements[elem_idx]
            min_pos = curr_pos
            max_pos = length - (len(selected_elements) - elem_idx)

            for pos in range(min_pos, max_pos + 1):
                new_peptide = curr_peptide.copy()
                new_peptide[pos] = element
                place_elements(pos + 1, elem_idx + 1, new_peptide)

        for selected_indices in combinations(range(len(non_null_elements)), k):
            selected_elements = [non_null_elements[i] for i in selected_indices]
            initial_peptide = [self.null_element] * length
            place_elements(0, 0, initial_peptide)

        return result

    def generate_all_descendants(self, peptide: Peptide) -> List[Peptide]:
        """Generate all possible descendants of a peptide that preserve relative order.

        Args:
            peptide (Peptide): The peptide to generate descendants for.

        Returns:
            List[Peptide]: A list of all possible descendant peptides.
        """
        peptides = []
        non_null_count = self.count_non_null(peptide)

        for k in range(non_null_count + 1):
            peptides_with_k = self.generate_descendants_with_k_elements(peptide, k)
            peptides.extend(peptides_with_k)

        return peptides

    def add_peptide(self, peptide: Peptide) -> None:
        """Add a peptide to the hierarchy and compute its relationships.

        Args:
            peptide (Peptide): The peptide to add.
        """
        level = self.count_non_null(peptide)
        self.levels[level].add(peptide)
        direct_desc = self.get_direct_descendants(peptide)
        self.descendants[peptide].update(direct_desc)

        for desc in direct_desc:
            self.ancestors[desc].add(peptide)

    def add_peptides(self, peptides: List[Peptide]) -> None:
        """Add multiple peptides to the hierarchy.

        Args:
            peptides (List[Peptide]): The list of peptides to add.
        """
        for peptide in peptides:
            self.add_peptide(peptide)

    def get_peptides_by_level(self, level: int) -> Set[Peptide]:
        """Get all peptides with a specific number of non-null elements.

        Args:
            level (int): The level to get peptides for.

        Returns:
            Set[Peptide]: A set of peptides at the specified level.
        """
        return self.levels[level]

    def get_level(self, peptide: Peptide) -> int:
        """Get the level (number of non-null elements) of a peptide.

        Args:
            peptide (Peptide): The peptide to get the level for.

        Returns:
            int: The level of the peptide.
        """
        return self.count_non_null(peptide)

    def get_ancestors(self, peptide: Peptide) -> Set[Peptide]:
        """Get all peptides that can have elements replaced to get this peptide.

        Args:
            peptide (Peptide): The peptide to get ancestors for.

        Returns:
            Set[Peptide]: A set of ancestor peptides.
        """
        return self.ancestors[peptide]

    def get_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """Get direct descendants of a peptide.

        Args:
            peptide (Peptide): The peptide to get descendants for.

        Returns:
            Set[Peptide]: A set of direct descendant peptides.
        """
        return self.descendants[peptide]

    def set_peptide_value(self, peptide: Peptide, value: V) -> None:
        """Set a value for a specific peptide.

        Args:
            peptide (Peptide): The peptide to set the value for.
            value (V): The value to set.
        """
        self.peptide_values[peptide] = value

    def set_peptide_values(self, values: Dict[Peptide, V]) -> None:
        """Set values for multiple peptides at once.

        Args:
            values (Dict[Peptide, V]): A dictionary mapping peptides to values.
        """
        self.peptide_values.update(values)

    def get_peptide_value(self, peptide: Peptide) -> Optional[V]:
        """Get the value associated with a peptide.

        Args:
            peptide (Peptide): The peptide to get the value for.

        Returns:
            Optional[V]: The value associated with the peptide, or None if not set.
        """
        return self.peptide_values.get(peptide)

    def visualize_hierarchy(
        self, figsize=(12, 8), node_size=2000,
        with_values: bool = False,
        save_path: Optional[str] = None,
        color_scheme: Optional[Dict[int, str]] = None
    ) -> None:
        """Visualize a Hierarchy object using NetworkX and Matplotlib.

        Args:
            figsize (tuple): Tuple of (width, height) for the figure.
            node_size (int): Size of nodes in the visualization.
            with_values (bool): Whether to display sequence values in nodes.
            save_path (Optional[str]): Optional path to save the visualization.
            color_scheme (Optional[Dict[int, str]]): Optional dictionary mapping levels to colors.
        """
        G = nx.DiGraph()
        max_level = max(self.levels.keys())

        if color_scheme is None:
            colors = list(mcolors.TABLEAU_COLORS.values())
            color_scheme = {
                level: colors[i % len(colors)] for i, level in enumerate(range(max_level + 1))
            }

        pos = {}
        for level in range(max_level + 1):
            peptides = self.get_peptides_by_level(level)
            if not peptides:
                continue

            y = (max_level - level) / max_level
            for i, pep in enumerate(sorted(peptides)):
                x = (i + 1) / (len(peptides) + 1)
                pos[pep] = (x, y)

                if with_values:
                    value = self.get_peptide_value(pep)
                    label = f"{'.'.join(str(x) for x in pep)}\n{value:.2f}" \
                        if value is not None else '.'.join(str(x) for x in pep)
                else:
                    label = '.'.join(str(x) for x in pep)

                G.add_node(pep, label=label, level=level, color=color_scheme[level])

        for pep in G.nodes():
            descendants = self.get_descendants(pep)
            for desc in descendants:
                G.add_edge(pep, desc)

        plt.figure(figsize=figsize)
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}

        nx.draw(G, pos, with_labels=True, labels=labels, node_color=node_colors,
                node_size=node_size, arrowsize=20, font_size=10, font_weight='bold',
                edge_color='gray', arrows=True)

        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=color, markersize=10,
                                     label=f'Level {level}')
                          for level, color in color_scheme.items()]
        plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))

        plt.title("Hierarchy Visualization")

        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        else:
            plt.show()

        plt.close()
