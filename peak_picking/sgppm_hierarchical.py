from dataclasses import dataclass, field
import numpy as np
from typing import List, Union, Dict, Tuple

from .building_block import BuildingBlock
from .chromatogram import Chromatogram
from .chromatogram_analyzer import ChromatogramAnalyzer
from .hierarchy import Hierarchy
from .sgppm import SimpleGaussianPeakPickingModel
from .sgppm_config import SGPPMConfig

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
        elution_times: Dict[Tuple[BuildingBlock, ...], float] = {}
        peak_intensities: Dict[Tuple[BuildingBlock, ...], float] = {}

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

        # Process chromatograms by level, starting from simplest (most Nulls)
        results = []
        for level in range(len(base_sequence) + 1):
            sequences = sequence_hierarchy.get_sequences_by_level(level)
            level_chromatograms = [
                sequence_to_chrom[seq] for seq in sequences
                if seq in sequence_to_chrom
            ]

            if level_chromatograms:
                # Process this level's chromatograms
                processed_chroms = self._process_level(
                    level_chromatograms,
                    level,
                    sequence_hierarchy,
                    elution_times,
                    peak_intensities
                )

                # Update elution times and intensities
                for chrom in processed_chroms:
                    if chrom.picked_peak:
                        sequence_tuple = tuple(chrom.building_blocks)
                        elution_times[sequence_tuple] = chrom.picked_peak.peak_metrics['time']
                        peak_intensities[sequence_tuple] = chrom.picked_peak.peak_metrics['height']

                results.extend(processed_chroms)

        return results[0] if len(chromatograms) == 1 else results

    def _process_level(
        self,
        chromatograms: List[Chromatogram],
        level: int,
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float],
        peak_intensities: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Process chromatograms at a specific level of the hierarchy"""
        # Prepare chromatograms (baseline correction etc.)
        chromatograms = self._prepare_chromatograms(chromatograms)

        # Analyze signal properties
        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)

        # For sequences with non-zero level, use information from simpler sequences
        if level > 0:
            self._adjust_search_parameters(chromatograms, sequence_hierarchy, elution_times)

        # Find peaks with adjusted parameters
        chromatograms = self._find_peaks(chromatograms)

        # Select peaks considering hierarchy constraints
        chromatograms = self._hierarchical_peak_selection(
            chromatograms,
            sequence_hierarchy,
            elution_times,
            peak_intensities
        )

        return chromatograms

    def _adjust_search_parameters(
        self,
        chromatograms: List[Chromatogram],
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float]
    ):
        """Adjust peak search parameters based on elution times of simpler sequences"""
        for chrom in chromatograms:
            sequence = tuple(chrom.building_blocks)

            # Get all descendants and their elution times
            descendants = sequence_hierarchy.get_descendants(sequence)
            valid_descendant_times = [
                elution_times[desc] for desc in descendants
                if desc in elution_times
            ]

            if valid_descendant_times:
                # Use latest eluting descendant as reference
                latest_time = max(valid_descendant_times)

                # Set the search window
                min_time = latest_time + self.config.peak_time_threshold
                max_time = chrom.x[-1]

                # Find corresponding indices
                min_idx = np.searchsorted(chrom.x, min_time)
                max_idx = len(chrom.x)

                # Create search mask
                chrom.search_mask = np.zeros_like(chrom.y, dtype=bool)
                chrom.search_mask[min_idx:max_idx] = True

                # Zero out signal outside search window
                masked_signal = np.where(chrom.search_mask, chrom.y_corrected, 0)
                chrom.y_corrected = masked_signal

    def _hierarchical_peak_selection(
        self,
        chromatograms: List[Chromatogram],
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float],
        peak_intensities: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Select peaks considering hierarchical constraints"""
        for chrom in chromatograms:
            if not chrom.peaks:
                continue

            sequence = tuple(chrom.building_blocks)
            descendants = sequence_hierarchy.get_descendants(sequence)

            # Get maximum intensity from descendants
            max_descendant_intensity = max(
                [peak_intensities.get(desc, 0) for desc in descendants],
                default=0
            )

            valid_peaks = []
            for peak in chrom.peaks:
                peak_height = peak.peak_metrics['height']
                peak_time = peak.peak_metrics['time']

                # Check if peak meets basic criteria
                if (peak_height >= self.config.height_threshold and
                    peak_height >= chrom.y_corrected.max() * self.config.pick_rel_height):

                    # For higher levels, ensure peak is higher than descendants
                    if sequence_hierarchy.get_level(sequence) == 0 or peak_height > max_descendant_intensity:
                        # Check timing constraints relative to descendants
                        valid_timing = True
                        for desc in descendants:
                            if desc in elution_times:
                                if peak_time <= elution_times[desc] + self.config.peak_time_threshold:
                                    valid_timing = False
                                    break

                        if valid_timing:
                            valid_peaks.append(peak)

            # Select the latest eluting valid peak
            if valid_peaks:
                chrom.picked_peak = max(valid_peaks, key=lambda p: p.peak_metrics['time'])
            else:
                chrom.picked_peak = None

        return chromatograms

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
