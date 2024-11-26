from dataclasses import dataclass, field
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths, savgol_filter
from scipy.interpolate import interp1d
from typing import List, Dict, Tuple

from .building_block import BuildingBlock
from .chromatogram import Chromatogram
from .chromatogram_analyzer import ChromatogramAnalyzer
from .hierarchy import Hierarchy
from .peak import Peak
from .peak_analyzer import PeakAnalyzer
from .sgppm import SimpleGaussianPeakPickingModel
from .sgppm_config import SGPPMConfig

@dataclass
class HierarchicalSimpleGaussianPeakPickingModel(SimpleGaussianPeakPickingModel):
    config: SGPPMConfig = field(default_factory=SGPPMConfig)
    debug: bool = True

    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Override base class peak finding to incorporate search masks"""
        for chrom in chromatograms:
            if self.debug:
                print(f"\nFinding peaks for sequence: {'-'.join(bb.name for bb in chrom.building_blocks)}")
                print(f"Signal range: {np.min(chrom.y):.2f} to {np.max(chrom.y):.2f}")
                print(f"Corrected signal range: {np.min(chrom.y_corrected):.2f} to {np.max(chrom.y_corrected):.2f}")
                print(f"Height threshold: {chrom.y.max() * self.config.search_rel_height:.2f}")

            # Use scipy.signal.find_peaks with original signal height reference
            search_peaks, properties = find_peaks(
                chrom.y_corrected,
                height=chrom.y.max() * self.config.search_rel_height,
                rel_height=self.config.search_rel_height
            )

            if self.debug:
                print(f"Found {len(search_peaks)} initial peaks")

            fitted_peaks = []
            for idx, peak_idx in enumerate(search_peaks):
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
                    if self.debug:
                        print(f"Peak at time {peak_obj.peak_metrics['time']:.2f} passed fitting")
                peak_obj = PeakAnalyzer.analyze_peak(peak_obj, chrom)

            chrom.peaks = fitted_peaks

            if self.debug:
                print(f"Final peak count: {len(fitted_peaks)}")

        return chromatograms

    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """
        Fit a Gaussian curve to peak data with interpolation for smoother results.
        """
        if self.debug:
            print(f"\nFitting peak at time {peak.peak_metrics['time']:.2f}")
            print(f"Initial height: {peak.peak_metrics['height']:.2f}")
            print(f"Initial width: {peak.peak_metrics['width']:.2f}")

        left_idx = max(0, int(peak.peak_metrics['left_base_index']))
        right_idx = min(len(x) - 1, int(peak.peak_metrics['right_base_index']))

        section_x = x[left_idx:right_idx + 1]
        section_y = y[left_idx:right_idx + 1]

        if len(section_x) < 3:
            if self.debug:
                print("Not enough points for fitting")
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': 'Not enough points for fitting'
            })
            return peak

        try:
            # Create higher resolution x-values for interpolation
            interp_factor = 10
            x_interp = np.linspace(section_x[0], section_x[-1], len(section_x) * interp_factor)

            # Smooth the section data
            window_length = min(7, len(section_y) - (len(section_y) % 2 + 1))
            if window_length >= 3:
                section_y_smooth = savgol_filter(section_y, window_length, 2)
            else:
                section_y_smooth = section_y

            if self.debug:
                print(f"Window length for smoothing: {window_length}")

            # Interpolate the smoothed data
            interp_func = interp1d(section_x, section_y_smooth, kind='cubic', bounds_error=False, fill_value=0)
            y_interp = interp_func(x_interp)

            # Get peak properties from interpolated data
            peak_idx = np.argmax(y_interp)
            height = np.max(y_interp)
            mean = x_interp[peak_idx]

            # Width estimation using interpolated data
            peak_mask = y_interp > (height * 0.1)
            peak_indices = np.where(peak_mask)[0]
            if len(peak_indices) >= 2:
                width = (x_interp[peak_indices[-1]] - x_interp[peak_indices[0]]) / 4
            else:
                width = (section_x[-1] - section_x[0]) / 6

            if self.debug:
                print(f"Initial fit parameters:")
                print(f"Height: {height:.2f}")
                print(f"Mean: {mean:.2f}")
                print(f"Width: {width:.4f}")

            # Initial parameters with adjusted bounds
            p0 = [height, mean, width]
            bounds = (
                [height * 0.7, x_interp[0], width * 0.3],
                [height * 1.3, x_interp[-1], width * 2.0]
            )

            if self.debug:
                print("Fit bounds:")
                print(f"Height: [{bounds[0][0]:.2f}, {bounds[1][0]:.2f}]")
                print(f"Mean: [{bounds[0][1]:.2f}, {bounds[1][1]:.2f}]")
                print(f"Width: [{bounds[0][2]:.4f}, {bounds[1][2]:.4f}]")

            # Create weights for interpolated data
            weights = np.ones_like(x_interp)
            peak_region = (x_interp > mean - width * 2) & (x_interp < mean + width * 2)
            weights[peak_region] = 3.0
            weights[y_interp < height * 0.1] = 0.5

            # Fit using interpolated data
            popt, _ = curve_fit(
                gaussian_curve,
                x_interp,
                y_interp,
                p0=p0,
                bounds=bounds,
                sigma=1/weights,
                maxfev=5000,
                method='trf'
            )

            if self.debug:
                print("Final fit parameters:")
                print(f"Amplitude: {popt[0]:.2f}")
                print(f"Mean: {popt[1]:.2f}")
                print(f"Stddev: {popt[2]:.4f}")
                print(f"Stddev threshold: {self.config.stddev_threshold}")

            # Calculate residuals using original data points
            section_fit = gaussian_curve(section_x, *popt)
            residuals = np.sum((section_y - section_fit)**2)
            normalized_residuals = residuals / (height * len(section_y))

            peak.peak_metrics.update({
                'gaussian_residuals': normalized_residuals,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'approximation_curve': self._generate_interpolated_curve(x, x_interp, popt, left_idx, right_idx)
            })

            if self.debug:
                print(f"Normalized residuals: {normalized_residuals:.4f}")
                if popt[2] >= self.config.stddev_threshold:
                    print(f"Peak rejected: stddev {popt[2]:.4f} >= threshold {self.config.stddev_threshold}")
                else:
                    print("Peak accepted")

        except (RuntimeError, ValueError) as e:
            if self.debug:
                print(f"Fitting error: {str(e)}")
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': str(e)
            })

        return peak


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
            print(f"\nProcessing Level {level}")

        # Prepare chromatograms (baseline correction etc.)
        chromatograms = self._prepare_chromatograms(chromatograms)

        # Analyze signal properties
        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)
            if self.debug:
                sequence_str = '-'.join(bb.name for bb in chrom.building_blocks)
                print(f"\nAnalyzing {sequence_str}")
                print(f"Signal range: {np.min(chrom.y_corrected):.2f} to {np.max(chrom.y_corrected):.2f}")

        # For sequences with non-zero level, create search masks
        if level > 0:
            chromatograms = self._create_search_masks(
                chromatograms,
                sequence_hierarchy,
                elution_times
            )

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

    def _create_search_masks(
        self,
        chromatograms: List[Chromatogram],
        sequence_hierarchy: Hierarchy,
        elution_times: Dict[Tuple[BuildingBlock, ...], float]
    ) -> List[Chromatogram]:
        """Create search masks for chromatograms based on hierarchical relationships"""
        for chrom in chromatograms:
            sequence = tuple(chrom.building_blocks)
            sequence_str = '-'.join(bb.name for bb in sequence)

            if self.debug:
                print(f"\nCreating search mask for {sequence_str}")

            # Get all descendants and their elution times
            descendants = sequence_hierarchy.get_descendants(sequence)
            valid_descendant_times = [
                elution_times[desc] for desc in descendants
                if desc in elution_times
            ]

            if valid_descendant_times:
                # Use latest eluting descendant as reference
                latest_time = max(valid_descendant_times)
                min_time = latest_time + self.config.peak_time_threshold

                if self.debug:
                    desc_times = {'-'.join(d.name for d in desc): elution_times[desc]
                                for desc in descendants if desc in elution_times}
                    print(f"Descendant elution times: {desc_times}")
                    print(f"Latest descendant time: {latest_time:.2f}")
                    print(f"Minimum search time: {min_time:.2f}")

                # Create mask
                min_idx = np.searchsorted(chrom.x, min_time)
                chrom.search_mask = np.zeros_like(chrom.y, dtype=bool)
                chrom.search_mask[min_idx:] = True

                if self.debug:
                    print(f"Created mask with {np.sum(chrom.search_mask)} points")
                    masked_signal = chrom.y_corrected[chrom.search_mask]
                    if np.any(masked_signal > 0):
                        print(f"Signal in search window: {np.min(masked_signal[masked_signal > 0]):.2f} to {np.max(masked_signal):.2f}")
                    else:
                        print("No signal in search window")
            else:
                if self.debug:
                    print("No valid descendant times - using full signal range")
                chrom.search_mask = np.ones_like(chrom.y, dtype=bool)

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
