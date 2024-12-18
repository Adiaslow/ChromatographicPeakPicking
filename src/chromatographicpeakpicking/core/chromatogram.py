from dataclasses import dataclass, field
import numpy as np
from typing import List, Optional

from core.peak import Peak
from core.building_block import BuildingBlock
from metrics.chromatogram_metrics import ChromatogramMetrics

@dataclass
class Chromatogram:
    """Class to represent a chromatogram

    Attributes:
        x (np.ndarray): Time values of the chromatogram
        y (np.ndarray): Intensity values of the chromatogram
        y_corrected (np.ndarray): Corrected intensity values of the chromatogram
        search_mask (np.ndarray): Mask for searching for peaks in the chromatogram
        metrics (ChromatogramMetrics): Metrics of the chromatogram
        peaks (List[Peak]): List of peaks in the chromatogram
        picked_peak (Peak): Picked peak of the chromatogram
        building_blocks (List[BuildingBlock]): List of building blocks in the chromatogram

    Methods:
        length: Return the length of the chromatogram data
        has_peaks: Check if chromatogram has any peaks
        add_peak: Add a peak to the chromatogram
        clear_peaks: Clear all peaks
        get_peaks_in_range: Get peaks within a specified time range
        _validate_chromatograms: Check if the chromatograms are of type Chromatogram
        _validate_peaks: Check if the peicked peak and the time of the picked peak of the chromatograms are not None
        __getitem__: Allow dictionary-like access to metrics
        __setitem__: Allow dictionary-like setting of metrics
        __eq__: Check if two chromatograms are equal with respect to the time of their picked peaks
        __ne__: Check if two chromatograms are not equal with respect to the time of their picked peaks
        __lt__: Check if one chromatogram is less than another with respect to the time of their picked peaks
        __le__: Check if one chromatogram is less than or equal to another with respect to the time of their picked peaks
        __gt__: Check if one chromatogram is greater than another with respect to the time of their picked peaks
        __ge__: Check if one chromatogram is greater than or equal to another with respect to the time of their picked peaks
        __hash__: Return the hash value of the chromatogram
        __str__: Return the string representation of the chromatogram
        __repr__: Return the string representation of the chromatogram
    """
    # Raw data
    x: Optional[np.ndarray] = None
    y: Optional[np.ndarray] = None

    # Processed data
    y_corrected: Optional[np.ndarray] = None
    search_mask: Optional[np.ndarray] = None
    metrics: ChromatogramMetrics = field(default_factory=ChromatogramMetrics)

    # Peak information
    peaks: List[Peak] = field(default_factory=list)
    picked_peak: Optional[Peak] = None

    # Metadata
    building_blocks: Optional[List[BuildingBlock]] = None


    @property
    def length(self) -> Optional[int]:
        """Return the length of the chromatogram data"""
        return len(self.x) if self.x is not None else None


    @property
    def has_peaks(self) -> bool:
        """Check if chromatogram has any peaks"""
        return len(self.peaks) > 0


    def add_peak(self, peak: Peak) -> None:
        """Add a peak to the chromatogram"""
        if not isinstance(peak, Peak):
            raise TypeError("Peak must be of type Peak")
        self.peaks.append(peak)


    def add_peaks(self, peaks: List[Peak]) -> None:
        """Add multiple peaks to the chromatogram"""
        for peak in peaks:
            self.add_peak(peak)


    def clear_peaks(self) -> None:
        """Clear all peaks"""
        self.peaks.clear()
        self.picked_peak = None


    def get_peaks_in_range(self, start_time: float, end_time: float) -> List[Peak]:
        """Get peaks within a specified time range"""
        return [peak for peak in self.peaks
            if start_time <= peak['time'] <= end_time]


    def _validate_chromatograms(self, other) -> bool:
        """Check if the chromatograms are of type Chromatogram"""
        if not isinstance(other, Chromatogram):
            raise ValueError("Cannot compare Chromatogram with non-Chromatogram object")
        return True


    def validate_data(self) -> None:
        """Validate the core data arrays"""
        if self.x is not None and self.y is not None:
            if len(self.x) != len(self.y):
                raise ValueError("X and Y arrays must have same length")
            x_finite = np.isfinite(self.x).all()  # type: ignore
            y_finite = np.isfinite(self.y).all()  # type: ignore
            if not x_finite or not y_finite:
                raise ValueError("Arrays contain NaN or infinite values")


    def _validate_peak_times(self, other) -> bool:
        """Check if the time of the picked peak of the chromatograms are not None"""
        if self.picked_peak is None or other.picked_peak is None:
            raise ValueError("Cannot compare Chromatogram with no picked peaks")
        if self['time'] is None or other['time'] is None:  # Assuming Peak has a time property
            raise ValueError("Cannot compare Chromatogram with no picked peak times")
        return True


    def __getitem__(self, key: str) -> float:
            """Allow dictionary-like access to metrics.

            Args:
                key: Name of the metric to retrieve

            Returns:
                Value of the requested metric

            Raises:
                KeyError: If metric name doesn't exist
            """
            value = self.metrics.get_metric(key)
            if value is None:
                raise KeyError(f"Metric '{key}' not found")
            return value


    def __setitem__(self, key: str, value: float) -> None:
        """Allow dictionary-like setting of metrics.

        Args:
            key: Name of the metric to set
            value: Value to set for the metric
        """
        self.metrics.set_metric(key, value)


    def __eq__(self, other) -> bool:
        """Check if two chromatograms are equal with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self['time'] == other['time']
        return False


    def __ne__(self, other) -> bool:
        """Check if two chromatograms are not equal with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return not self.__eq__(other)
        return False


    def __lt__(self, other) -> bool:
        """Check if one chromatogram is less than the other with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self['time'] < other['time']
        return False


    def __le__(self, other) -> bool:
        """Check if one chromatogram is less than or equal to the other with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self['time'] <= other['time']
        return False


    def __gt__(self, other) -> bool:
        """Check if one chromatogram is greater than the other with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self['time'] > other['time']
        return False


    def __ge__(self, other) -> bool:
        """Check if one chromatogram is greater than or equal to the other with respect to the time of their picked peaks"""
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self['time'] >= other['time']
        return False

    def __hash__(self) -> int:
        """Return a hash of the chromatogram"""
        return hash((
            tuple(self.x) if self.x is not None else None,
            tuple(self.y) if self.y is not None else None
        ))

    def __str__(self) -> str:
        """Return a string representation of the chromatogram.
        Handles cases of:
        - No peaks
        - Single peak
        - Multiple peaks
        - With or without picked peak
        Includes times for all peaks
        """
        # Get number of peaks
        num_peaks = len(self.peaks) if self.peaks is not None else 0

        # Build peak count description
        if num_peaks == 0:
            peak_desc = "no peaks"
        elif num_peaks == 1:
            peak_desc = "1 peak"
        else:
            peak_desc = f"{num_peaks} peaks"

        # Add peak times if there are peaks
        if num_peaks > 0:
            peak_times = [f"{peak['time']:.2f}" for peak in self.peaks]
            peak_desc += f" at times {', '.join(peak_times)}"

        # Build picked peak description
        if self.picked_peak is None:
            picked_desc = "no picked peak"
        else:
            time = self.picked_peak['time']
            if time is not None:
                picked_desc = f"picked peak at time {time:.2f}"
            else:
                picked_desc = "picked peak (no time)"

        return f"Chromatogram with {peak_desc} and {picked_desc}"


    def __repr__(self) -> str:
        """Return a string representation of the chromatogram"""
        return self.__str__()
