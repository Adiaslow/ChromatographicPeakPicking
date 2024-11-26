from dataclasses import dataclass, field
import numpy as np
from typing import List, Union, Dict, Tuple

from .building_block import BuildingBlock
from .chromatogram import Chromatogram
from .chromatogram_analyzer import ChromatogramAnalyzer
from .hierarchy import Hierarchy
from .sgppm import SimpleGaussianPeakPickingModel
from .sgppm_config import SGPPMConfig

@dataclass
class HierarchicalSimpleGaussianPeakPickingModel(SimpleGaussianPeakPickingModel):
    config: SGPPMConfig = field(default_factory=SGPPMConfig)

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        # Create local hierarchy and elution times for this set of chromatograms
        sequence_hierarchy = Hierarchy(null_element=BuildingBlock(name='Null'))
        elution_times = {}

        # Generate mapping of building block tuples to chromatograms
        sequence_to_chrom = {
            tuple(chrom.building_blocks): chrom for chrom in chromatograms
        }

        # Get base sequence (one with most non-Null building blocks)
        base_sequence = max(
            sequence_to_chrom.keys(),
            key=lambda seq: sum(1 for x in seq if x.name != 'Null')
        )

        # Generate all valid sequences and add to hierarchy
        all_sequences = sequence_hierarchy.generate_all_descendants(base_sequence)
        all_sequences.append(base_sequence)
        sequence_hierarchy.add_sequences(all_sequences)

        # Process chromatograms by level
        results = []
        for level in range(len(base_sequence) + 1):
            sequences = sequence_hierarchy.get_sequences_by_level(level)
            level_chromatograms = [
                sequence_to_chrom[seq] for seq in sequences
                if seq in sequence_to_chrom
            ]

            if level_chromatograms:
                processed_chroms = self._process_level(
                    level_chromatograms,
                    level,
                    sequence_hierarchy,
                    elution_times
                )

                # Store elution times for processed chromatograms
                for chrom in processed_chroms:
                    if chrom.picked_peak:
                        sequence_tuple = tuple(chrom.building_blocks)
                        elution_times[sequence_tuple] = chrom.picked_peak.peak_metrics['time']

                results.extend(processed_chroms)

        # Update hierarchy with elution times
        sequence_hierarchy.set_sequence_values(elution_times)

        return results[0] if len(chromatograms) == 1 else results

    def _process_level(
        self,
        chromatograms: List[Chromatogram],
        level: int,
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Process chromatograms at a specific level of the hierarchy"""
        # Prepare chromatograms (baseline correction etc.)
        chromatograms = self._prepare_chromatograms(chromatograms)

        # Analyze chromatogram properties
        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)

        # For sequences with N elements, use information from simpler sequences
        if level > 0:
            self._adjust_search_parameters(chromatograms, level, sequence_hierarchy, elution_times)

        # Find and select peaks
        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        return chromatograms

    def _adjust_search_parameters(
        self,
        chromatograms: List[Chromatogram],
        level: int,
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float]
    ):
        """Adjust peak search parameters based on elution times of simpler sequences"""
        for chrom in chromatograms:
            sequence = tuple(chrom.building_blocks)

            # Get descendants (simpler sequences) and their elution times
            descendants = sequence_hierarchy.get_descendants(sequence)
            descendant_times = [
                elution_times[desc]
                for desc in descendants
                if desc in elution_times
            ]

            if descendant_times:
                # Find the latest eluting descendant
                latest_descendant_time = max(descendant_times)

                # Set minimum elution time for this sequence
                min_allowed_time = latest_descendant_time + self.config.peak_time_threshold

                # Calculate the time window where peaks should be searched
                peak_search_window = (
                    min_allowed_time,  # Start after the latest descendant plus threshold
                    chrom.x[-1]        # End at the last time point
                )

                # Store the search window in the chromatogram object
                chrom.search_window = peak_search_window

                # Apply the search window
                self._update_peak_constraints(chrom, peak_search_window)

    def _update_peak_constraints(self, chrom: Chromatogram, search_window: Tuple[float, float]):
        """
        Update the peak finding constraints based on the calculated search window.

        Args:
            chrom: Chromatogram to update
            search_window: Tuple of (min_time, max_time) for peak search
        """
        # Find indices corresponding to the search window times
        min_time_idx = np.searchsorted(chrom.x, search_window[0])
        max_time_idx = np.searchsorted(chrom.x, search_window[1])

        # Create a mask for the valid search region
        chrom.search_window = np.zeros_like(chrom.y, dtype=bool)
        chrom.search_window[min_time_idx:max_time_idx] = True
