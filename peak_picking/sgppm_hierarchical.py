from dataclasses import dataclass, field
import numpy as np
from typing import List, Dict, Tuple

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

    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Override base class peak finding to incorporate search masks"""
        for chrom in chromatograms:
            # Store original corrected signal
            original_y_corrected = chrom.y_corrected.copy()

            # Apply search mask if it exists
            if hasattr(chrom, 'search_window'):
                if self.debug:
                    print(f"Applying search mask: {np.sum(chrom.search_window)} points in search window")
                chrom.y_corrected = np.where(chrom.search_window, original_y_corrected, 0)

            # Call parent class peak finding
            chroms = super()._find_peaks([chrom])

            # Restore original signal
            chrom.y_corrected = original_y_corrected

            if self.debug and not chrom.peaks and hasattr(chrom, 'search_window'):
                print("No peaks found in search window")
                print(f"Search window contains signal: {np.any(chrom.y_corrected[chrom.search_window] > 0)}")
                if np.any(chrom.y_corrected > 0):
                    max_val = np.max(chrom.y_corrected)
                    max_masked = np.max(chrom.y_corrected[chrom.search_window]) if np.any(chrom.search_window) else 0
                    print(f"Max signal overall: {max_val:.2f}")
                    print(f"Max signal in search window: {max_masked:.2f}")
                    print(f"Search rel height threshold: {self.config.search_rel_height}")
                    print(f"Required height for detection: {max_val * self.config.search_rel_height:.2f}")

        return chromatograms

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
            if self.debug:
                sequence_str = '-'.join(bb.name for bb in chrom.building_blocks)
                print(f"\nProcessing {sequence_str}")
                print(f"Signal range: {np.min(chrom.y_corrected):.2f} to {np.max(chrom.y_corrected):.2f}")

        # For sequences with non-zero level, use information from simpler sequences
        if level > 0:
            self._adjust_search_parameters(chromatograms, sequence_hierarchy, elution_times)

        # Find peaks
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
                chrom.search_window = np.zeros_like(chrom.y, dtype=bool)
                chrom.search_window[min_idx:max_idx] = True

                if self.debug:
                    print(f"Search window covers {np.sum(chrom.search_window)} points")
                    if np.any(chrom.y_corrected[chrom.search_window] > 0):
                        print(f"Maximum signal in search window: {np.max(chrom.y_corrected[chrom.search_window]):.2f}")
                    else:
                        print("No signal in search window")

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
