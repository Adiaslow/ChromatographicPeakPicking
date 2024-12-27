# src/chromatographicpeakpicking/core/domain/peak.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from uuid import uuid4
import numpy as np

@dataclass(frozen=True)
class Peak:
    """
    Represents a chromatographic peak with its characteristics and metrics.

    This class encapsulates all information about a detected peak, including
    its position, shape parameters, and quality metrics.
    """

    # Core peak characteristics
    apex_time: float
    apex_intensity: float
    start_time: float
    end_time: float

    # Peak shape parameters
    height: float
    area: float
    width_at_half_height: Optional[float] = None
    asymmetry_factor: Optional[float] = None

    # Peak quality metrics
    signal_to_noise: Optional[float] = None
    resolution: Optional[float] = None
    peak_capacity: Optional[float] = None

    # Gaussian fit parameters
    gaussian_params: Optional[Dict[str, float]] = None

    # Additional data
    raw_times: Optional[np.ndarray] = None
    raw_intensities: Optional[np.ndarray] = None
    baseline: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Validate peak data after initialization."""
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be less than end time")
        if not (self.start_time <= self.apex_time <= self.end_time):
            raise ValueError("Apex time must be between start and end times")
        if self.height <= 0:
            raise ValueError("Height must be positive")
        if self.area <= 0:
            raise ValueError("Area must be positive")

        # Validate array data if present
        if self.raw_times is not None and self.raw_intensities is not None:
            if len(self.raw_times) != len(self.raw_intensities):
                raise ValueError("Raw times and intensities must have same length")

    @property
    def width(self) -> float:
        """Calculate peak width."""
        return self.end_time - self.start_time

    @property
    def retention_time(self) -> float:
        """Get retention time (apex time)."""
        return self.apex_time

    @property
    def symmetry(self) -> Optional[float]:
        """Calculate peak symmetry if possible."""
        if self.asymmetry_factor is not None:
            return 1 / self.asymmetry_factor
        return None

    def get_gaussian_fit(self) -> Optional[Dict[str, float]]:
        """Get Gaussian fit parameters if available."""
        return self.gaussian_params

    def with_gaussian_fit(self, params: Dict[str, float]) -> 'Peak':
        """Create new peak instance with Gaussian fit parameters."""
        return Peak(
            id=self.id,
            apex_time=self.apex_time,
            apex_intensity=self.apex_intensity,
            start_time=self.start_time,
            end_time=self.end_time,
            height=self.height,
            area=self.area,
            width_at_half_height=self.width_at_half_height,
            asymmetry_factor=self.asymmetry_factor,
            signal_to_noise=self.signal_to_noise,
            resolution=self.resolution,
            peak_capacity=self.peak_capacity,
            gaussian_params=params,
            raw_times=self.raw_times,
            raw_intensities=self.raw_intensities,
            baseline=self.baseline,
            metadata=self.metadata
        )

    def with_quality_metrics(self,
                           signal_to_noise: Optional[float] = None,
                           resolution: Optional[float] = None,
                           peak_capacity: Optional[float] = None) -> 'Peak':
        """Create new peak instance with updated quality metrics."""
        return Peak(
            id=self.id,
            apex_time=self.apex_time,
            apex_intensity=self.apex_intensity,
            start_time=self.start_time,
            end_time=self.end_time,
            height=self.height,
            area=self.area,
            width_at_half_height=self.width_at_half_height,
            asymmetry_factor=self.asymmetry_factor,
            signal_to_noise=signal_to_noise or self.signal_to_noise,
            resolution=resolution or self.resolution,
            peak_capacity=peak_capacity or self.peak_capacity,
            gaussian_params=self.gaussian_params,
            raw_times=self.raw_times,
            raw_intensities=self.raw_intensities,
            baseline=self.baseline,
            metadata=self.metadata
        )

    def overlaps_with(self, other: 'Peak') -> bool:
        """Check if this peak overlaps with another peak."""
        return not (self.end_time <= other.start_time or
                   other.end_time <= self.start_time)

    def get_overlap_percentage(self, other: 'Peak') -> float:
        """Calculate percentage overlap with another peak."""
        if not self.overlaps_with(other):
            return 0.0

        overlap_start = max(self.start_time, other.start_time)
        overlap_end = min(self.end_time, other.end_time)
        overlap_width = overlap_end - overlap_start

        return (overlap_width / min(self.width, other.width)) * 100

    def __eq__(self, other: object) -> bool:
        """Compare peaks for equality."""
        if not isinstance(other, Peak):
            return NotImplemented
        return (
            abs(self.apex_time - other.apex_time) < 1e-6 and
            abs(self.apex_intensity - other.apex_intensity) < 1e-6 and
            abs(self.start_time - other.start_time) < 1e-6 and
            abs(self.end_time - other.end_time) < 1e-6
        )

    def __hash__(self) -> int:
        """Generate hash for peak."""
        return hash((
            round(self.apex_time, 6),
            round(self.apex_intensity, 6),
            round(self.start_time, 6),
            round(self.end_time, 6)
        ))
