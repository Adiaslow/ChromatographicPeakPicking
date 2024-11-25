from dataclasses import dataclass
import numpy as np
from typing import Union, List

@dataclass
class BaselineCorrector:
    """Class for baseline correction of chromatograms

    Attributes:
        None

    Methods:
        correct_baseline: Correct baseline of chromatogram using specified method
        _asymmetric_least_squares_smoothing: Baseline correction using asymmetric least squares smoothing
        _sliding_window_minimum: Baseline correction using sliding window minimum
    """
    @staticmethod
    def correct_baseline(
        y: np.array,
        method: str = "ALSS"
    ) -> np.array:
        if method == "ALSS":
            return BaselineCorrector._asymmetric_least_squares_smoothing(y)
        elif method == "SWM":
            return BaselineCorrector._sliding_window_minimum(y)
        else:
            raise ValueError("Invalid baseline correction method")


    @staticmethod
    def _asymmetric_least_squares_smoothing(
        y: np.ndarray,
        lam: float = 1e2,
        p: float = 0.001,
        niter: int = 10
    ) -> np.ndarray:
        """Baseline correction using asymmetric least squares smoothing

        Args:
            y (np.ndarray): intensity values of the chromatogram
            lam (float): smoothness parameter. Default is 1e2
            p (float): asymmetry parameter. Default is 0.001
            niter (int): number of iterations. Default is 10

        Returns:
            y - z (np.ndarray): baseline corrected chromatogram

        Raises:
            None
        """
        L: int = len(y)
        D: np.ndarray = np.diff(np.eye(L), 2)
        w: np.ndarray = np.ones(L)
        z: np.ndarray = np.zeros(L)
        for i in range(niter):
            W: np.ndarray = np.diag(w)
            Z: np.ndarray = W + lam * D.dot(D.transpose())
            z: np.ndarray = np.linalg.solve(Z, w * y)
            w: np.ndarray = p * (y > z) + (1-p) * (y < z)
        return y - z


    @staticmethod
    def _sliding_window_minimum(
        y: np.ndarray,
        window_length: int = 3
    ) -> np.ndarray:
        """Baseline correction using sliding window minimum

        Args:
            y (np.ndarray): intensity values of the chromatogram
            window_length (int): length of the sliding window. Default is 3

        Returns:
            y_corrected (np.ndarray): baseline corrected chromatogram

        Raises:
            ValueError: if window_length is not a positive odd integer
        """
        if window_length <= 0 or window_length % 2 == 0:
            raise ValueError("window_length must be a positive odd integer")

        half_window = window_length // 2
        y_padded = np.pad(y, (half_window, half_window), mode='edge')

        y_min = np.min(
            np.lib.stride_tricks.sliding_window_view(y_padded, window_length),
            axis=1
        )

        y_diff = y - y_min
        y_corrected = y_diff.copy()
        y_corrected /= np.max(y_corrected)

        non_zero_mask = y_diff != 0
        y_corrected[non_zero_mask] = y[non_zero_mask]

        return y_corrected
