from dataclasses import dataclass, field
import numpy as np
from typing import List, Union, Dict, Tuple

from .chromatogram import Chromatogram
from .hierarchy import Hierarchy
from .peak_analyzer import PeakAnalyzer
from .sgppm import SimpleGaussianPeakPickingModel
from .sgppm_config import SGPPMConfig

@dataclass
class HierarchicalSimpleGaussianPeakPickingModel(SimpleGaussianPeakPickingModel):
    config: SGPPMConfig = field(default_factory=SGPPMConfig)
    sequence_hierarchy: Hierarchy = field(init=False)
    elution_times: Dict[Tuple[str, ...], float] = field(default_factory=dict)

    def __post_init__(self):
        self.sequence_hierarchy = Hierarchy(null_element='N')

    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """
        Override of parent class _find_peaks to respect search windows.
        """
        for chrom in chromatograms:
            # If we have a search window, apply the mask
            if hasattr(chrom, 'search_mask'):
                y_to_search = chrom.y_corrected.copy()
                # Zero out regions outside the search window
                y_to_search[~chrom.search_mask] = 0

                search_peaks, properties = find_peaks(
                    y_to_search,
                    height=chrom.y.max() * self.config.search_rel_height,
                    rel_height=self.config.search_rel_height
                )
            else:
                # Default behavior if no search window is defined
                search_peaks, properties = find_peaks(
                    chrom.y_corrected,
                    height=chrom.y.max() * self.config.search_rel_height,
                    rel_height=self.config.search_rel_height
                )

            fitted_peaks = []
            for idx, peak_idx in enumerate(search_peaks):
                # Skip peaks outside our search window if it exists
                if hasattr(chrom, 'search_mask') and not chrom.search_mask[peak_idx]:
                    continue

                peak_obj = Peak()
                width_points = peak_widths(chrom.y_corrected, [peak_idx], rel_height=0.5)
                left_idx = int(width_points[2][0])
                right_idx = int(width_points[3][0])

                peak_obj.peak_metrics.update({
                    'index': peak_idx,
                    'time': chrom.x[peak_idx],
                    'height': chrom.y_corrected[peak_idx],
                    'left_base_index': left_idx,
                    'right_base_index': right_idx,
                    'left_base_time': chrom.x[left_idx],
                    'right_base_time': chrom.x[right_idx],
                    'width': chrom.x[right_idx] - chrom.x[left_idx]
                })

                peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)
                if peak_obj.peak_metrics.get('fit_stddev', float('inf')) < self.config.stddev_threshold:
                    fitted_peaks.append(peak_obj)
                peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)

            chrom.peaks = fitted_peaks
        return chromatograms

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        """
        Pick peaks hierarchically, starting from sequences with most N elements
        and using that information to inform peak picking of more complex sequences.
        """
        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        # Generate mapping of sequences to chromatograms
        sequence_to_chrom = {
            tuple(chrom.sequence): chrom for chrom in chromatograms
        }

        # Get base sequence (one with most non-N elements)
        base_sequence = max(sequence_to_chrom.keys(),
                          key=lambda seq: sum(1 for x in seq if x != 'N'))

        # Generate all valid sequences and add to hierarchy
        all_sequences = self.sequence_hierarchy.generate_all_descendants(base_sequence)
        all_sequences.append(base_sequence)
        self.sequence_hierarchy.add_sequences(all_sequences)

        # Process chromatograms by level (number of N elements)
        results = []
        for level in range(len(base_sequence) + 1):
            sequences = self.sequence_hierarchy.get_sequences_by_level(level)
            level_chromatograms = [
                sequence_to_chrom[seq] for seq in sequences
                if seq in sequence_to_chrom
            ]

            if level_chromatograms:
                # Process this level's chromatograms
                processed_chroms = self._process_level(level_chromatograms, level)

                # Store elution times for processed chromatograms
                for chrom in processed_chroms:
                    if chrom.picked_peak:
                        self.elution_times[tuple(chrom.sequence)] = chrom.picked_peak.peak_metrics['time']

                results.extend(processed_chroms)

        # Update hierarchy with elution times
        self.sequence_hierarchy.set_sequence_values(self.elution_times)

        return results[0] if len(chromatograms) == 1 else results

    def _process_level(self, chromatograms: List[Chromatogram], level: int) -> List[Chromatogram]:
        """Process chromatograms at a specific level of the hierarchy"""
        # Prepare chromatograms (baseline correction etc.)
        chromatograms = self._prepare_chromatograms(chromatograms)

        # Analyze chromatogram properties
        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)

        # For sequences with N elements, use information from simpler sequences
        if level > 0:
            self._adjust_search_parameters(chromatograms, level)

        # Find and select peaks
        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        return chromatograms

    def _adjust_search_parameters(self, chromatograms: List[Chromatogram], level: int):
        """
        Adjust peak search parameters based on elution times of simpler sequences.
        Ensures that parent sequences elute after their descendants by at least peak_time_threshold.

        Args:
            chromatograms: List of chromatograms to process
            level: Current hierarchy level being processed
        """
        for chrom in chromatograms:
            sequence = tuple(chrom.sequence)

            # Get descendants (simpler sequences) and their elution times
            descendants = self.sequence_hierarchy.get_descendants(sequence)
            descendant_times = [
                self.elution_times[desc]
                for desc in descendants
                if desc in self.elution_times
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

                # Store the search window in the chromatogram object for use in peak finding
                chrom.search_window = peak_search_window

                # Modify peak finding logic in _find_peaks to use this window
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
        chrom.search_mask = np.zeros_like(chrom.y, dtype=bool)
        chrom.search_mask[min_time_idx:max_time_idx] = True
