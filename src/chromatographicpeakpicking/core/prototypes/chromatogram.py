# src/chromatographicpeakpicking/core/prototypes/chromatogram.py
"""
Module: chromatogram

This module defines the Chromatogram class, which represents a chromatogram
with its time series data and associated peaks. The Chromatogram class follows the
Prototype Pattern to allow for efficient cloning of instances with optional modifications.

Design Patterns:
    - Prototype Pattern: Used to create new objects by copying an existing object (the prototype).

Rationale:
    - Efficiency: Cloning an existing object can be more efficient than creating a new one from
        scratch, especially when the object has already been initialized with a complex state.
    - Simplicity: The Prototype Pattern simplifies object creation by allowing for the reuse of
        existing objects with optional modifications.
    - Flexibility: Provides flexibility in creating new objects based on an existing prototype with
        slight variations, reducing the need for multiple constructors or factory methods.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import uuid4
import numpy as np
import copy
from .peak import Peak

@dataclass(frozen=True)
class Chromatogram:
    """
    Represents a chromatogram with its time series data and associated peaks.

    This class encapsulates all information about a chromatogram, including
    raw data, detected peaks, baseline, and metadata.

    Attributes:
        time (np.ndarray): The time points of the chromatogram.
        intensity (np.ndarray): The intensity values of the chromatogram.
        peaks (List[Peak]): The list of detected peaks in the chromatogram.
        baseline (Optional[np.ndarray]): The baseline values of the chromatogram.
        noise_level (Optional[float]): The noise level of the chromatogram.
        y_corrected (Optional[np.ndarray]): The baseline-corrected intensity values.
        search_mask (Optional[np.ndarray]): The search mask for peak detection.
        properties (Dict[str, Any]): Additional properties of the chromatogram.
        picked_peak (Optional[Peak]): The selected peak of interest.
        metadata (Dict[str, Any]): Additional metadata about the chromatogram.
        id (str): A unique identifier for the chromatogram.
    """

    # Core data
    time: np.ndarray
    intensity: np.ndarray

    # Processing results
    peaks: List[Peak] = field(default_factory=list)
    baseline: Optional[np.ndarray] = None
    noise_level: Optional[float] = None
    y_corrected: Optional[np.ndarray] = None
    search_mask: Optional[np.ndarray] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    picked_peak: Optional[Peak] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate chromatogram data after initialization."""
        if len(self.time) != len(self.intensity):
            raise ValueError("Time and intensity arrays must have the same length")
        if len(self.time) < 2:
            raise ValueError("Chromatogram must have at least 2 points")
        if not isinstance(self.time, np.ndarray):
            object.__setattr__(self, 'time', np.array(self.time))
        if not isinstance(self.intensity, np.ndarray):
            object.__setattr__(self, 'intensity', np.array(self.intensity))
        if self.baseline is not None and len(self.baseline) != len(self.time):
            raise ValueError("Baseline must have the same length as time array")

    @property
    def length(self) -> int:
        """Get the number of data points."""
        return len(self.time)

    @property
    def duration(self) -> float:
        """Get the total chromatogram duration."""
        return self.time[-1] - self.time[0]

    @property
    def num_peaks(self) -> int:
        """Get the number of detected peaks."""
        return len(self.peaks)

    def get_intensity_range(self) -> tuple[float, float]:
        """Get the intensity range."""
        return float(np.min(self.intensity)), float(np.max(self.intensity))

    def get_time_range(self) -> tuple[float, float]:
        """Get the time range."""
        return float(self.time[0]), float(self.time[-1])

    def get_signal_at_time(self, t: float) -> Optional[float]:
        """Get the intensity value at a specific time point."""
        idx = np.searchsorted(self.time, t)
        if idx >= len(self.time):
            return None
        return float(self.intensity[idx])

    def get_peaks_in_range(self, start_time: float, end_time: float) -> List[Peak]:
        """Get peaks within the specified time range."""
        return [
            peak for peak in self.peaks
            if start_time <= peak.time <= end_time
        ]

    def clone(self, **kwargs: Any) -> 'Chromatogram':
        """
        Clone the current chromatogram, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            Chromatogram: A new Chromatogram instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        # Set a new unique ID unless explicitly provided in kwargs
        new_instance_id = kwargs.get('id', str(uuid4()))
        object.__setattr__(new_instance, 'id', new_instance_id)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance

    def with_peaks(self, peaks: List[Peak]) -> 'Chromatogram':
        """Create a new chromatogram instance with updated peaks."""
        return self.clone(peaks=peaks)

    def with_baseline(self, baseline: np.ndarray) -> 'Chromatogram':
        """Create a new chromatogram instance with baseline."""
        if len(baseline) != len(self.time):
            raise ValueError("Baseline must have the same length as the time array")
        return self.clone(baseline=baseline)

    def with_properties(self, **kwargs: Any) -> 'Chromatogram':
        """Create a new chromatogram instance with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs) -> 'Chromatogram':
        """Create a new chromatogram instance with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def get_corrected_intensity(self) -> np.ndarray:
        """Get baseline-corrected intensity values."""
        if self.baseline is None:
            return self.intensity
        return self.intensity - self.baseline

    def slice(self, start_time: float, end_time: float) -> 'Chromatogram':
        """Create a new chromatogram containing only data within the specified time range."""
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")

        mask = (self.time >= start_time) & (self.time <= end_time)
        if not np.any(mask):
            raise ValueError("No data points in the specified time range")

        # Slice time and intensity arrays
        new_time = self.time[mask]
        new_intensity = self.intensity[mask]
        new_baseline = self.baseline[mask] if self.baseline is not None else None

        # Filter peaks within range
        new_peaks = self.get_peaks_in_range(start_time, end_time)

        return Chromatogram(
            time=new_time,
            intensity=new_intensity,
            peaks=new_peaks,
            baseline=new_baseline,
            noise_level=self.noise_level,
            y_corrected=self.y_corrected,
            search_mask=self.search_mask,
            properties=self.properties,
            picked_peak=self.picked_peak,
            metadata=self.metadata
        )

    def resample(self, num_points: int) -> 'Chromatogram':
        """Create a new chromatogram with resampled data points."""
        if num_points < 2:
            raise ValueError("Number of points must be at least 2")

        # Create new time points
        start, end = self.time[0], self.time[-1]
        new_time = np.linspace(start, end, num_points)

        # Resample intensity and baseline
        new_intensity = np.interp(new_time, self.time, self.intensity)
        new_baseline = None
        if self.baseline is not None:
            new_baseline = np.interp(new_time, self.time, self.baseline)

        return Chromatogram(
            time=new_time,
            intensity=new_intensity,
            peaks=self.peaks,  # Peaks are preserved as they store absolute times
            baseline=new_baseline,
            noise_level=self.noise_level,
            y_corrected=self.y_corrected,
            search_mask=self.search_mask,
            properties=self.properties,
            picked_peak=self.picked_peak,
            metadata=self.metadata
        )

    def smooth(self, window_length: int = 5, polyorder: int = 2) -> 'Chromatogram':
        """Create a new chromatogram with smoothed intensity values using Savitzky-Golay filter."""
        from scipy.signal import savgol_filter

        if window_length >= len(self.time):
            raise ValueError("Window length must be less than chromatogram length")
        if window_length % 2 == 0:
            raise ValueError("Window length must be odd")
        if polyorder >= window_length:
            raise ValueError("Polynomial order must be less than window length")

        smoothed_intensity = savgol_filter(
            self.intensity,
            window_length=window_length,
            polyorder=polyorder
        )

        return Chromatogram(
            time=self.time,
            intensity=smoothed_intensity,
            peaks=self.peaks,
            baseline=self.baseline,
            noise_level=self.noise_level,
            y_corrected=self.y_corrected,
            search_mask=self.search_mask,
            properties=self.properties,
            picked_peak=self.picked_peak,
            metadata=self.metadata
        )

    def normalize(self, method: str = 'max') -> 'Chromatogram':
        """Create a new chromatogram with normalized intensity values."""
        if method not in ['max', 'area', 'sum']:
            raise ValueError("Normalization method must be 'max', 'area', or 'sum'")

        if method == 'max':
            factor = np.max(np.abs(self.intensity))
        elif method == 'area':
            factor = np.trapezoid(np.abs(self.intensity), self.time)
        else:  # sum
            factor = np.sum(np.abs(self.intensity))

        if factor == 0:
            raise ValueError("Cannot normalize: all intensity values are zero")

        normalized_intensity = self.intensity / factor
        normalized_baseline = self.baseline / factor if self.baseline is not None else None

        # Adjust peak intensities
        normalized_peaks = [
            Peak(
                time=peak.time,
                index=peak.index,
                intensity=float(peak.intensity / factor),
                properties=peak.properties,
                metadata=peak.metadata,
                id=peak.id
            ) for peak in self.peaks
        ]

        return Chromatogram(
            time=self.time,
            intensity=normalized_intensity,
            peaks=normalized_peaks,
            baseline=normalized_baseline,
            noise_level=float(self.noise_level / factor) if self.noise_level is not None else None,
            y_corrected=self.y_corrected,
            search_mask=self.search_mask,
            properties=self.properties,
            picked_peak=self.picked_peak,
            metadata=self.metadata
        )

    def __len__(self) -> int:
        """Get the number of data points."""
        return len(self.time)

    def __eq__(self, other: object) -> bool:
        """Compare chromatograms for equality."""
        if not isinstance(other, Chromatogram):
            return NotImplemented
        return (
            np.array_equal(self.time, other.time) and
            np.array_equal(self.intensity, other.intensity)
        )

    def __str__(self) -> str:
        """String representation of chromatogram."""
        return (
            f"Chromatogram(points={len(self)}, "
            f"peaks={len(self.peaks)}, "
            f"time_range={self.get_time_range()})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of chromatogram."""
        return (
            f"Chromatogram(id='{self.id}', "
            f"points={len(self)}, "
            f"peaks={len(self.peaks)}, "
            f"time_range={self.get_time_range()}, "
            f"intensity_range={self.get_intensity_range()})"
        )
