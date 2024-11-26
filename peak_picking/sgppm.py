from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths, savgol_filter
from scipy.interpolate import interp1d
from typing import List, Union

from .baseline_corrector import BaselineCorrector
from .chromatogram import Chromatogram
from .chromatogram_analyzer import ChromatogramAnalyzer
from .gaussian_curve import gaussian_curve
from .peak import Peak
from .peak_analyzer import PeakAnalyzer
from .peak_picker import PeakPicker
from .sgppm_config import SGPPMConfig

@dataclass
class SimpleGaussianPeakPickingModel(PeakPicker[SGPPMConfig]):
    config: SGPPMConfig = SGPPMConfig()
    debug: bool = True

    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        if isinstance(chromatograms, Chromatogram):
            chromatograms = [chromatograms]

        chromatograms = self._prepare_chromatograms(chromatograms)

        for chrom in chromatograms:
            chrom.signal_metrics = ChromatogramAnalyzer.analyze_chromatogram(chrom)

        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        return chromatograms[0] if len(chromatograms) == 1 else chromatograms

    def _prepare_chromatograms(self, chromatograms: List[Chromatogram], method=SGPPMConfig.correction_method) -> List[Chromatogram]:
        for chrom in chromatograms:
            chrom.y_corrected = BaselineCorrector.correct_baseline(
                y=chrom.y,
                method=self.config.correction_method
            )
        return chromatograms

    from dataclasses import dataclass, field
    import numpy as np
    from typing import List, Union, Dict, Tuple
    from scipy.signal import find_peaks, peak_widths

    from .building_block import BuildingBlock
    from .chromatogram import Chromatogram
    from .chromatogram_analyzer import ChromatogramAnalyzer
    from .hierarchy import Hierarchy
    from .sgppm import SimpleGaussianPeakPickingModel
    from .sgppm_config import SGPPMConfig
    from .peak import Peak

    @dataclass
    class HierarchicalSimpleGaussianPeakPickingModel(SimpleGaussianPeakPickingModel):
        config: SGPPMConfig = field(default_factory=SGPPMConfig)
        debug: bool = False

        def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
            """Modified peak finding with detailed failure analysis"""
            for chrom in chromatograms:
                sequence_str = '-'.join(bb.name for bb in chrom.building_blocks)
                if self.debug:
                    print(f"\nFinding peaks for sequence: {sequence_str}")
                    print(f"Signal range: {np.min(chrom.y_corrected):.2f} to {np.max(chrom.y_corrected):.2f}")
                    print(f"Config parameters:")
                    print(f"  Height threshold: {self.config.height_threshold}")
                    print(f"  Width min/max: {self.config.width_min}/{self.config.width_max}")
                    print(f"  Gaussian residuals threshold: {self.config.gaussian_residuals_threshold}")
                    print(f"  StdDev threshold: {self.config.stddev_threshold}")

                # Find initial peaks
                search_peaks, properties = find_peaks(
                    chrom.y_corrected,
                    height=chrom.y.max() * self.config.search_rel_height,
                    rel_height=self.config.search_rel_height,
                    distance=int(len(chrom.x) * self.config.min_distance_factor)
                )

                if self.debug:
                    print(f"\nFound {len(search_peaks)} initial peaks")

                fitted_peaks = []
                for peak_idx in search_peaks:
                    if self.debug:
                        print(f"\nAnalyzing peak at index {peak_idx} (time {chrom.x[peak_idx]:.2f})")
                        print(f"Initial height: {chrom.y_corrected[peak_idx]:.2f}")

                    # Create peak object
                    peak_obj = Peak()

                    # Find peak boundaries
                    half_height = chrom.y_corrected[peak_idx] / 2
                    left_idx = peak_idx
                    while left_idx > 0 and chrom.y_corrected[left_idx - 1] > half_height:
                        left_idx -= 1

                    right_idx = peak_idx
                    while right_idx < len(chrom.y_corrected) - 1 and chrom.y_corrected[right_idx + 1] > half_height:
                        right_idx += 1

                    # Ensure minimum width
                    min_points = 3
                    if right_idx - left_idx < min_points:
                        padding = (min_points - (right_idx - left_idx)) // 2
                        left_idx = max(0, left_idx - padding)
                        right_idx = min(len(chrom.y_corrected) - 1, right_idx + padding)

                    if self.debug:
                        print(f"Peak boundaries:")
                        print(f"  Left idx/time: {left_idx}/{chrom.x[left_idx]:.2f}")
                        print(f"  Right idx/time: {right_idx}/{chrom.x[right_idx]:.2f}")
                        print(f"  Points in peak: {right_idx - left_idx + 1}")

                    # Calculate peak metrics
                    width = chrom.x[right_idx] - chrom.x[left_idx]
                    peak_obj.peak_metrics.update({
                        'index': peak_idx,
                        'time': chrom.x[peak_idx],
                        'height': chrom.y_corrected[peak_idx],
                        'left_base_index': left_idx,
                        'right_base_index': right_idx,
                        'left_base_time': chrom.x[left_idx],
                        'right_base_time': chrom.x[right_idx],
                        'width': width
                    })

                    if self.debug:
                        print(f"Initial metrics:")
                        print(f"  Height: {peak_obj.peak_metrics['height']:.2f}")
                        print(f"  Width: {width:.4f}")

                    # Check basic width criteria before fitting
                    if width < self.config.width_min:
                        if self.debug:
                            print(f"Peak rejected: Width {width:.4f} < minimum {self.config.width_min}")
                        continue

                    if width > self.config.width_max:
                        if self.debug:
                            print(f"Peak rejected: Width {width:.4f} > maximum {self.config.width_max}")
                        continue

                    # Fit Gaussian
                    peak_obj = self._fit_gaussian(chrom.x, chrom.y_corrected, peak_obj)

                    if self.debug:
                        print("\nGaussian fit results:")
                        if 'fit_error' in peak_obj.peak_metrics:
                            print(f"Fitting error: {peak_obj.peak_metrics['fit_error']}")
                        else:
                            print(f"  Amplitude: {peak_obj.peak_metrics.get('fit_amplitude', 'N/A')}")
                            print(f"  Mean: {peak_obj.peak_metrics.get('fit_mean', 'N/A')}")
                            print(f"  StdDev: {peak_obj.peak_metrics.get('fit_stddev', 'N/A')}")
                            print(f"  Residuals: {peak_obj.peak_metrics.get('gaussian_residuals', 'N/A')}")

                    # Validate the fit
                    if 'fit_error' in peak_obj.peak_metrics:
                        if self.debug:
                            print("Peak rejected: Fitting failed")
                        continue

                    residuals = peak_obj.peak_metrics.get('gaussian_residuals', float('inf'))
                    if residuals >= self.config.gaussian_residuals_threshold:
                        if self.debug:
                            print(f"Peak rejected: Residuals {residuals:.4f} >= threshold {self.config.gaussian_residuals_threshold}")
                        continue

                    stddev = peak_obj.peak_metrics.get('fit_stddev', float('inf'))
                    if stddev >= self.config.stddev_threshold:
                        if self.debug:
                            print(f"Peak rejected: StdDev {stddev:.4f} >= threshold {self.config.stddev_threshold}")
                        continue

                    # Peak passed all criteria
                    if self.debug:
                        print("Peak accepted: Passed all criteria")
                    fitted_peaks.append(peak_obj)

                chrom.peaks = fitted_peaks

                if self.debug:
                    print(f"\nFinal results for {sequence_str}:")
                    print(f"Accepted {len(fitted_peaks)} peaks out of {len(search_peaks)} candidates")
                    for peak in fitted_peaks:
                        print(f"  Time: {peak.peak_metrics['time']:.2f}")
                        print(f"  Height: {peak.peak_metrics['height']:.2f}")
                        print(f"  Width: {peak.peak_metrics['width']:.2f}")

            return chromatograms


    def _fit_gaussian(self, x: np.ndarray, y: np.ndarray, peak: Peak) -> Peak:
        """
        Fit a Gaussian curve to peak data with interpolation for smoother results.

        Args:
            x: x-axis data
            y: y-axis data (baseline corrected)
            peak: Peak object containing initial peak metrics
        """
        left_idx = max(0, int(peak.peak_metrics['left_base_index']))
        right_idx = min(len(x) - 1, int(peak.peak_metrics['right_base_index']))

        section_x = x[left_idx:right_idx + 1]
        section_y = y[left_idx:right_idx + 1]

        if len(section_x) < 3:  # Need at least 3 points for fitting
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

            # Initial parameters with adjusted bounds
            p0 = [height, mean, width]
            bounds = (
                [height * 0.7, x_interp[0], width * 0.3],
                [height * 1.3, x_interp[-1], width * 2.0]
            )

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

            # Generate the full curve
            fitted_curve = np.zeros_like(x)

            # Calculate the high-resolution curve
            x_high_res = np.linspace(x[0], x[-1], len(x) * interp_factor)
            curve_high_res = gaussian_curve(x_high_res, *popt)

            # Apply damping at edges if needed
            if left_idx > 0:
                left_mask = x_high_res < x[left_idx]
                damping = np.exp(-(x[left_idx] - x_high_res[left_mask]) / width)
                curve_high_res[left_mask] *= damping

            if right_idx < len(x) - 1:
                right_mask = x_high_res > x[right_idx]
                damping = np.exp(-(x_high_res[right_mask] - x[right_idx]) / width)
                curve_high_res[right_mask] *= damping

            # Interpolate back to original grid
            interp_func = interp1d(x_high_res, curve_high_res, kind='cubic', bounds_error=False, fill_value=0)
            fitted_curve = interp_func(x)

            # Calculate residuals using original data points
            section_fit = gaussian_curve(section_x, *popt)
            residuals = np.sum((section_y - section_fit)**2)
            normalized_residuals = residuals / (height * len(section_y))

            peak.peak_metrics.update({
                'gaussian_residuals': normalized_residuals,
                'fit_amplitude': popt[0],
                'fit_mean': popt[1],
                'fit_stddev': popt[2],
                'approximation_curve': fitted_curve
            })

        except (RuntimeError, ValueError) as e:
            peak.peak_metrics.update({
                'gaussian_residuals': float('inf'),
                'fit_error': str(e)
            })

        return peak

    def _generate_interpolated_curve(self, x, x_interp, popt, left_idx, right_idx):
        """Generate smooth curve using interpolation and proper decay to zero"""
        # Generate high-resolution curve for the entire x range
        x_full_interp = np.linspace(x[0], x[-1], len(x) * 10)
        curve_full = np.zeros_like(x_full_interp)

        # Find indices corresponding to the section boundaries in interpolated space
        left_interp = np.searchsorted(x_full_interp, x[left_idx])
        right_interp = np.searchsorted(x_full_interp, x[right_idx])

        # Generate the main fitted section with high resolution
        section_mask = slice(left_interp, right_interp)
        curve_full[section_mask] = gaussian_curve(x_full_interp[section_mask], *popt)

        # Apply smooth decay outside the fitting region
        if left_interp > 0:
            left_x = x_full_interp[:left_interp]
            left_y = gaussian_curve(left_x, *popt)
            damping = np.exp(-(np.arange(len(left_x))[::-1]) / (len(left_x) / 3))
            curve_full[:left_interp] = left_y * damping

        if right_interp < len(x_full_interp):
            right_x = x_full_interp[right_interp:]
            right_y = gaussian_curve(right_x, *popt)
            damping = np.exp(-np.arange(len(right_x)) / (len(right_x) / 3))
            curve_full[right_interp:] = right_y * damping

        # Interpolate back to original x grid
        interp_func = interp1d(x_full_interp, curve_full, kind='cubic', bounds_error=False, fill_value=0)
        return interp_func(x)

    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Override to add debugging of base class peak selection"""
        for chrom in chromatograms:
            if self.debug:
                print(f"\nSelecting peaks for {'-'.join(bb.name for bb in chrom.building_blocks)}")
                if chrom.peaks:
                    max_y = np.max(chrom.y_corrected)
                    print(f"Number of peaks to consider: {len(chrom.peaks)}")
                    print(f"Maximum signal: {max_y:.2f}")
                    print(f"Height threshold: {self.config.height_threshold}")
                    print(f"Relative height threshold: {self.config.pick_rel_height}")
                    for peak in chrom.peaks:
                        height = peak.peak_metrics['height']
                        print(f"\nEvaluating peak:")
                        print(f"  Time: {peak.peak_metrics['time']:.2f}")
                        print(f"  Height: {height:.2f}")
                        print(f"  Meets absolute threshold: {height >= self.config.height_threshold}")
                        print(f"  Meets relative threshold: {height >= max_y * self.config.pick_rel_height}")
                else:
                    print("No peaks to select from")

            # Process peaks normally
            if not chrom.peaks:
                continue

            max_y = np.max(chrom.y_corrected)
            valid_peaks = []

            for peak in chrom.peaks:
                peak_height = peak.peak_metrics['height']
                if (peak_height >= self.config.height_threshold and
                    peak_height >= max_y * self.config.pick_rel_height):
                    valid_peaks.append(peak)
                    if self.debug:
                        print(f"Peak at time {peak.peak_metrics['time']:.2f} accepted")

            if valid_peaks:
                best_peak = max(valid_peaks, key=lambda p: p.peak_metrics['time'])
                chrom.picked_peak = best_peak
                if self.debug:
                    print(f"Selected peak at time {best_peak.peak_metrics['time']:.2f}")
            else:
                if self.debug:
                    print("No peaks met selection criteria")
                chrom.picked_peak = None

        return chromatograms
