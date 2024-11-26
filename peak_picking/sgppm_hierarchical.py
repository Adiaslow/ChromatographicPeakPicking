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
                if self.debug:
                    print(f"\nProcessing Level {level} Sequences:")

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
                    sequence = tuple(chrom.building_blocks)
                    sequence_str = '-'.join(bb.name for bb in sequence)

                    if chrom.picked_peak:
                        elution_times[sequence] = chrom.picked_peak.peak_metrics['time']
                        peak_intensities[sequence] = chrom.picked_peak.peak_metrics['height']
                        if self.debug:
                            print(f"Sequence: {sequence_str}, Peak picked at time {chrom.picked_peak.peak_metrics['time']:.2f} with height {chrom.picked_peak.peak_metrics['height']:.2f}")
                    else:
                        if self.debug:
                            print(f"Sequence: {sequence_str}, No peak picked")

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
            sequence_str = '-'.join(bb.name for bb in sequence)

            # Get all descendants and their elution times
            descendants = sequence_hierarchy.get_descendants(sequence)
            valid_descendant_times = [
                elution_times[desc] for desc in descendants
                if desc in elution_times
            ]

            if valid_descendant_times:
                # Use latest eluting descendant as reference
                latest_time = max(valid_descendant_times)

                if self.debug:
                    desc_times = {'-'.join(d.name for d in desc): elution_times[desc]
                                for desc in descendants if desc in elution_times}
                    print(f"\nAdjusting search parameters for {sequence_str}:")
                    print(f"Descendant elution times: {desc_times}")
                    print(f"Latest descendant time: {latest_time:.2f}")
                    print(f"Setting minimum search time to: {latest_time + self.config.peak_time_threshold:.2f}")

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
            sequence = tuple(chrom.building_blocks)
            sequence_str = '-'.join(bb.name for bb in sequence)

            if self.debug:
                print(f"\nAnalyzing peaks for sequence: {sequence_str}")
                if not chrom.peaks:
                    print("No peaks detected in initial peak finding")
                else:
                    print(f"Found {len(chrom.peaks)} potential peaks")

            if not chrom.peaks:
                continue

            descendants = sequence_hierarchy.get_descendants(sequence)
            max_descendant_intensity = max(
                [peak_intensities.get(desc, 0) for desc in descendants],
                default=0
            )

            if self.debug and descendants:
                desc_intensities = {'-'.join(d.name for d in desc): peak_intensities.get(desc, 0)
                                  for desc in descendants}
                print(f"Descendant intensities: {desc_intensities}")
                print(f"Maximum descendant intensity: {max_descendant_intensity:.2f}")

            valid_peaks = []
            for peak in chrom.peaks:
                peak_height = peak.peak_metrics['height']
                peak_time = peak.peak_metrics['time']

                if self.debug:
                    print(f"\nEvaluating peak at time {peak_time:.2f} with height {peak_height:.2f}")

                # Check basic height threshold
                if peak_height < self.config.height_threshold:
                    if self.debug:
                        print(f"Peak rejected: Height {peak_height:.2f} below threshold {self.config.height_threshold}")
                    continue

                # Check relative height threshold
                if peak_height < chrom.y_corrected.max() * self.config.pick_rel_height:
                    if self.debug:
                        print(f"Peak rejected: Height {peak_height:.2f} below relative threshold "
                              f"({self.config.pick_rel_height * 100}% of max {chrom.y_corrected.max():.2f})")
                    continue

                # For higher levels, check intensity relative to descendants
                if sequence_hierarchy.get_level(sequence) > 0:
                    if peak_height <= max_descendant_intensity:
                        if self.debug:
                            print(f"Peak rejected: Height {peak_height:.2f} not greater than "
                                  f"maximum descendant intensity {max_descendant_intensity:.2f}")
                        continue

                # Check timing constraints relative to descendants
                valid_timing = True
                for desc in descendants:
                    if desc in elution_times:
                        desc_time = elution_times[desc]
                        min_required_time = desc_time + self.config.peak_time_threshold
                        if peak_time <= min_required_time:
                            if self.debug:
                                desc_str = '-'.join(d.name for d in desc)
                                print(f"Peak rejected: Time {peak_time:.2f} not after descendant "
                                      f"{desc_str} time {desc_time:.2f} plus threshold {self.config.peak_time_threshold}")
                            valid_timing = False
                            break

                if valid_timing:
                    if self.debug:
                        print("Peak passed all criteria")
                    valid_peaks.append(peak)

            # Select the latest eluting valid peak
            if valid_peaks:
                chrom.picked_peak = max(valid_peaks, key=lambda p: p.peak_metrics['time'])
                if self.debug:
                    print(f"\nSelected peak at time {chrom.picked_peak.peak_metrics['time']:.2f} "
                          f"with height {chrom.picked_peak.peak_metrics['height']:.2f}")
            else:
                chrom.picked_peak = None
                if self.debug:
                    print("\nNo valid peaks found after applying all criteria")

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
