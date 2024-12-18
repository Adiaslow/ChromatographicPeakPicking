# External imports
from dataclasses import dataclass
import numpy as np
from typing import Optional

# Internal imports
from ..configs.aals_config import AALSConfig
from .baseline_corrector import BaselineCorrector
from ..core.chromatogram import Chromatogram

@dataclass
class AALS(BaselineCorrector[AALSConfig]):
    """Adaptive Asymmetric Least Squares baseline correction algorithm.

    This implementation follows the method described in:
    Eilers, P. H., & Boelens, H. F. (2005). Baseline correction with
    asymmetric least squares smoothing.

    The algorithm iteratively estimates a baseline by penalizing positive
    deviations more heavily than negative ones, while maintaining smoothness
    through a second derivative constraint.

    Attributes:
        config: Configuration object for the AALS algorithm

    Methods:
        correct_baseline: Perform baseline correction on chromatogram data
    """
    config: AALSConfig = AALSConfig()

    def correct_baseline(self, chrom: Chromatogram) -> Chromatogram:
        """Perform baseline correction on chromatogram data.

        Args:
            chrom: Chromatogram object containing the signal to be corrected

        Returns:
            Chromatogram: Chromatogram with corrected baseline in y_corrected attribute

        Raises:
            ValueError: If input signal contains NaN or infinite values
            LinAlgError: If the linear system cannot be solved
        """
        # Input validation
        y: np.ndarray = chrom.y
        if not np.all(np.isfinite(y)):
            raise ValueError("Input signal contains NaN or infinite values")

        # Initialize variables
        L: int = len(y)
        if L < 3:
            raise ValueError("Signal length must be at least 3 points")

        # Construct second difference matrix
        D: np.ndarray = np.diff(np.eye(L), n=2, axis=0)

        # Initialize weights and baseline estimate
        w: np.ndarray = np.ones(L)
        z: Optional[np.ndarray] = None

        # Iterative estimation
        for _ in range(self.config.niter):
            # Construct weighted diagonal matrix
            W: np.ndarray = np.diag(w)

            # Construct system matrix
            Z: np.ndarray = W + self.config.lam * D.T @ D

            try:
                # Solve for new baseline estimate
                z = np.linalg.solve(Z, w * y)

                # Update weights based on residuals
                w = np.where(y > z,
                           self.config.p,      # Positive residuals
                           (1-self.config.p))  # Negative residuals
            except np.linalg.LinAlgError as e:
                raise np.linalg.LinAlgError(
                    "Failed to solve linear system. Try adjusting lambda parameter."
                ) from e

        if z is None:
            raise RuntimeError("Algorithm failed to produce baseline estimate")

        # Store corrected signal
        chrom.y_corrected = y - z
        return chrom
