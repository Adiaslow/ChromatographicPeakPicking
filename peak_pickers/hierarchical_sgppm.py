from dataclasses import dataclass, field
import numpy as np
from typing import List, Dict, Tuple, Union

from ..core.building_block import BuildingBlock
from ..core.chromatogram import Chromatogram
from ..core.hierarchy import Hierarchy
from .sgppm import SGPPM
from ..configs.sgppm_config import SGPPMConfig

@dataclass
class HierarchicalSGPPM(SGPPM):
    config: SGPPMConfig = field(default_factory=SGPPMConfig)
    debug: bool = True

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        # Create local hierarchy and elution times for this set of chromatograms
        sequence_hierarchy = Hierarchy(null_element=BuildingBlock(name='Null'))
        elution_times: Dict[Tuple[BuildingBlock, ...], float] = {}
        peak_intensities: Dict[Tuple[BuildingBlock, ...], float] = {}

        # Generate mapping of building block tuples to chromatograms
        sequence_to_chrom = {
            tuple(chrom.building_blocks or ()): chrom for chrom in chromatograms
        }

        # Get base sequence and generate hierarchy
        base_sequence = max(
            sequence_to_chrom.keys(),
            key=lambda seq: sum(bool(x.name != 'Null')
                            for x in seq)
        )
        all_sequences = sequence_hierarchy.generate_all_descendants(base_sequence)
        all_sequences.append(base_sequence)
        sequence_hierarchy.add_sequences(all_sequences)

        # Process chromatograms by level
        results = []
        for level in range(len(base_sequence) + 1):
            sequences = sequence_hierarchy.get_sequences_by_level(level)
            if level_chromatograms := [
                sequence_to_chrom[seq]
                for seq in sequences
                if seq in sequence_to_chrom
            ]:
                if self.debug:
                    print(f"\nProcessing Level {level}")

                # Process this level
                processed_chroms = self._process_level(
                    level_chromatograms,
                    level,
                    sequence_hierarchy,
                    elution_times,
                    peak_intensities
                )

                # Update times and intensities
                for chrom in processed_chroms:
                    sequence = tuple(chrom.building_blocks or ())
                    if chrom.picked_peak:
                        elution_times[sequence] = chrom.picked_peak['time']
                        peak_intensities[sequence] = chrom.picked_peak['height']
                        if self.debug:
                            print(f"Sequence: {'-'.join(bb.name for bb in sequence if bb.name != None)}")
                            print(f"  Peak time: {chrom.picked_peak['time']:.2f}")
                            print(f"  Peak height: {chrom.picked_peak['height']:.2f}")

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
        if self.debug:
            print(f"\nProcessing level {level} chromatograms")

        # Prepare chromatograms
        chromatograms = self._prepare_chromatograms(chromatograms)

        # For higher levels, create search masks
        if level > 0:
            chromatograms = self._apply_hierarchy_constraints(
                chromatograms, sequence_hierarchy, elution_times
            )

        # Use base class peak finding
        chromatograms = super()._find_peaks(chromatograms)

        # Apply hierarchical peak selection
        chromatograms = self._hierarchical_peak_selection(
            chromatograms, sequence_hierarchy, peak_intensities
        )

        return chromatograms

    def _apply_hierarchy_constraints(
        self,
        chromatograms: List[Chromatogram],
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Apply hierarchy constraints to chromatograms"""
        for chrom in chromatograms:
            sequence = tuple(chrom.building_blocks or ())

            # Get descendants and their times
            descendants = sequence_hierarchy.get_descendants(sequence)
            if valid_times := [
                elution_times[desc]
                for desc in descendants
                if desc in elution_times
            ]:
                min_time = max(valid_times) + self.config.peak_time_threshold
                min_idx = np.searchsorted(chrom.x, min_time)

                # Zero out signal before minimum time
                if chrom.y_corrected is not None:
                    chrom.y_corrected[:min_idx] = 0

                if self.debug:
                    print(f"Sequence: {'-'.join(bb.name for bb in sequence if bb.name != None)}")
                    print(f"  Minimum allowed time: {min_time:.2f}")
                    if chrom.y_corrected is not None:
                        remaining_signal = np.any(chrom.y_corrected[min_idx:] > 0)
                        print(f"  Signal remains after constraint: {remaining_signal}")

        return chromatograms

    def _hierarchical_peak_selection(
        self,
        chromatograms: List[Chromatogram],
        sequence_hierarchy: Hierarchy,
        peak_intensities: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Select peaks considering hierarchical relationships"""
        for chrom in chromatograms:
            if not chrom.peaks:
                continue

            sequence = tuple(chrom.building_blocks or ())
            level = sequence_hierarchy.get_level(sequence)

            # Get maximum intensity from descendants
            descendants = sequence_hierarchy.get_descendants(sequence)
            max_descendant_intensity = max(
                (peak_intensities.get(desc, 0) for desc in descendants), default=0
            )

            # Filter peaks based on hierarchy constraints
            valid_peaks = []
            for peak in chrom.peaks:
                peak_height = peak['height']

                # Basic threshold check
                if peak_height >= self.config.height_threshold and (level == 0 or peak_height > max_descendant_intensity):
                    valid_peaks.append(peak)

            # Select latest eluting valid peak
            if valid_peaks:
                chrom.picked_peak = max(valid_peaks, key=lambda p: p['time'])
                if self.debug:
                    print(f"Selected peak for {'-'.join(bb.name for bb in sequence if bb.name != None)}")
                    print(f"  Time: {chrom.picked_peak['time'] if chrom.picked_peak else np.NaN:.2f}")
                    print(f"  Height: {chrom.picked_peak['height'] if chrom.picked_peak else np.NaN:.2f}")
            else:
                chrom.picked_peak = None

        return chromatograms
