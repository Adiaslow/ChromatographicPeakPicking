# src/chromatographicpeakpicking/analysis/baseline/swm.py
"""
This module implements the Sliding Window Minimum (SWM) baseline correction algorithm.
"""

from dataclasses import dataclass, field
import numpy as np
from src.chromatographicpeakpicking.core.protocols.configurable import Configurable
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig, ConfigMetadata, ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

@dataclass
class SWMConfig(BaseConfig):
    """Configuration for Sliding Window Minimum baseline correction."""
    def __init__(self, window_length: int = 3, padding_mode: str = 'edge'):
        super().__init__(metadata=ConfigMetadata(
            name="SWMConfig",
            version="1.0",
            description="Configuration for SWM Baseline Corrector",
            defaults={"window_length": 3, "padding_mode": "edge"},
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={"window_length": window_length, "padding_mode": padding_mode})

@dataclass
class SWM(Configurable[SWMConfig]):
    """Sliding Window Minimum baseline correction algorithm.

    This algorithm identifies the baseline of a chromatogram by calculating local
    minima within a sliding window of specified length. The baseline is then
    subtracted from the signal and points where the difference is positive retain
    their original values, while others are set to zero.

    The process involves:
        1. Padding the signal based on the window length
        2. Computing local minima using a sliding window
        3. Subtracting the baseline from the original signal
        4. Keeping original values where difference is positive, else zero
        5. Filtering out zero-intensity points

    Attributes:
        config: Configuration object containing window_length and padding_mode parameters
    """
    config: SWMConfig = field(default_factory=SWMConfig)

    def configure(self, config: SWMConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def get_metadata(self) -> ConfigMetadata:
        return self.config.metadata

    def validate_config(self, config: SWMConfig) -> ValidationResult:
        errors = []
        if not isinstance(config.parameters["window_length"], int):
            errors.append("Window length must be an integer.")
        if config.parameters["window_length"] <= 0:
            errors.append("Window length must be positive.")
        if config.parameters["window_length"] % 2 == 0:
            errors.append("Window length must be an odd integer.")
        if config.parameters["padding_mode"] not in [
            "reflect",
            "constant",
            "nearest",
            "mirror",
            "wrap"
        ]:
            errors.append(f"Invalid padding mode: {config.parameters['padding_mode']}")

        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Perform baseline correction using sliding window minima method."""
        y = chromatogram.intensity

        # Validate inputs
        self._validate_inputs(y)

        # Calculate window parameters
        half_window = self.config.parameters["window_length"] // 2

        # Pad signal
        y_pad = self._pad_signal(y, half_window)

        # Calculate baseline
        y_min = self._compute_baseline(y_pad)

        # Subtract baseline
        y_diff = y - y_min

        # Keep original values where difference > 0, else 0
        y_corrected = np.where(y_diff > 0, y, 0)

        # Filter out zero points
        non_zero_mask = y_corrected != 0
        if not np.any(non_zero_mask):
            raise ValueError("No non-zero points remain after baseline correction")

        return Chromatogram(
            time=chromatogram.time,
            intensity=chromatogram.intensity,
            y_corrected=y_corrected[non_zero_mask],
            metadata=chromatogram.metadata,
            peaks=chromatogram.peaks,
            baseline=y_min
        )

    def _validate_inputs(self, y: np.ndarray) -> None:
        """Validate input parameters and signal."""
        if not isinstance(self.config.parameters["window_length"], int):
            raise TypeError("Window length must be an integer.")
        if self.config.parameters["window_length"] <= 0:
            raise ValueError("Window length must be positive.")
        if self.config.parameters["window_length"] % 2 == 0:
            raise ValueError("Window length must be an odd integer.")
        if len(y) == 0:
            raise ValueError("Input signal is empty.")
        if not np.all(np.isfinite(y)):
            raise ValueError("Input signal contains NaN or infinite values.")
        if len(y) < self.config.parameters["window_length"]:
            raise ValueError(
                f"Signal length ({len(y)}) must be >= window length "
                f"({self.config.parameters['window_length']})"
            )

    def _pad_signal(self, y: np.ndarray, half_window: int) -> np.ndarray:
        """Pad the input signal according to config."""
        try:
            return np.pad(
                y,
                (half_window, half_window),
                mode=self.config.parameters["padding_mode"])
        except ValueError as e:
            raise ValueError("Invalid padding mode: " + \
                f"{self.config.parameters['padding_mode']}") from e

    def _compute_baseline(self, y_padded: np.ndarray) -> np.ndarray:
        """Compute the baseline using sliding window minimum."""
        try:
            window_view = np.lib.stride_tricks.sliding_window_view(
                y_padded, self.config.parameters["window_length"]
            )
            return np.min(window_view, axis=1)
        except Exception as e:
            raise RuntimeError("Failed to compute sliding window minimum") from e
