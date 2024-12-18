from dataclasses import dataclass, field
import numpy as np

from baseline_correctors.Ibaseline_corrector import IBaselineCorrector
from core.chromatogram import Chromatogram
from configs.swm_config import SWMConfig

@dataclass
class SWM(IBaselineCorrector[SWMConfig]):
    """Sliding Window Minima baseline correction algorithm.

    This algorithm identifies the baseline of a chromatogram by calculating local
    minima within a sliding window of specified length. The baseline is then
    subtracted from the signal and points where the difference is positive retain
    their original values, while others are set to zero.

    The process involves:
        1. Padding the signal based on the window length
        2. Computing local minima using a sliding window
        3. Subtracting the baseline from the original signal
        4. Kepp original values where difference is positive, else zero
        5. Filtering out zero-intensity points

    Attributes:
        config: Configuration object containing window_length and padding_mode parameters
    """
    config: SWMConfig = field(default_factory=SWMConfig)

    def _validate_inputs(self, y: np.ndarray) -> None:
        """Validate input parameters and signal.

        Args:
            y: Input signal array

        Raises:
            TypeError: If window_length is not an integer
            ValueError: If window_length is not positive odd integer
            ValueError: If input signal is empty
            ValueError: If input signal contains invalid values
        """
        if not isinstance(self.config.window_length, int):
            raise TypeError("window_length must be an integer")

        if self.config.window_length <= 0:
            raise ValueError("window_length must be positive")

        if self.config.window_length % 2 == 0:
            raise ValueError("window_length must be odd")

        if len(y) == 0:
            raise ValueError("Input signal is empty")

        if not np.all(np.isfinite(y)):
            raise ValueError("Input signal contains NaN or infinite values")

        if len(y) < self.config.window_length:
            raise ValueError(
                f"Signal length ({len(y)}) must be >= window_length ({self.config.window_length})"
            )

    def _pad_signal(self, y: np.ndarray, half_window: int) -> np.ndarray:
        """Pad the input signal according to config.

        Args:
            y: Input signal array
            half_window: Half of the window length

        Returns:
            Padded signal array

        Raises:
            ValueError: If padding_mode is invalid
        """
        try:
            return np.pad(y, (half_window, half_window), mode=self.config.padding_mode)
        except ValueError as e:
            raise ValueError(f"Invalid padding_mode: {self.config.padding_mode}") from e

    def _compute_baseline(self, y_padded: np.ndarray) -> np.ndarray:
        """Compute the baseline using sliding window minimum.

        Args:
            y_padded: Padded input signal

        Returns:
            Computed baseline array

        Raises:
            RuntimeError: If sliding window computation fails
        """
        try:
            window_view = np.lib.stride_tricks.sliding_window_view(
                y_padded,
                self.config.window_length
            )
            return np.min(window_view, axis=1)
        except Exception as e:
            raise RuntimeError("Failed to compute sliding window minimum") from e

    def correct_baseline(self, chrom: Chromatogram) -> Chromatogram:
        """Perform baseline correction using sliding window minima method.

        Args:
            chrom: Chromatogram object containing the signal to be corrected

        Returns:
            Chromatogram with baseline-corrected signal in y_corrected attribute

        Raises:
            TypeError: If window_length is not an integer
            ValueError: If window_length is not positive odd integer
            ValueError: If input signal is empty or invalid
            ValueError: If padding_mode is invalid
            ValueError: If no non-zero points remain after correction
            RuntimeError: If baseline computation fails
        """
        y = chrom.y

        # Validate inputs
        self._validate_inputs(y)

        # Calculate window parameters
        half_window = self.config.window_length // 2

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

        chrom.y_corrected = y_corrected[non_zero_mask]
        return chrom
