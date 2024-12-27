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
                raw_times=self.raw_times,
                raw_intensities=self.raw_intensities,
                baseline=self.baseline,
                metadata=self.metadata,
                gaussian_params=params
            )
