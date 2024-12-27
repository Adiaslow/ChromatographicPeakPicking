# src/chromatographicpeakpicking/analysis/baseline/aals.py
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from ...core.protocols.baseline_corrector import BaselineCorrector
from ...core.domain.chromatogram import Chromatogram

@dataclass
class AALSCorrector(BaselineCorrector):
    """Asymmetric Least Squares Smoothing baseline correction."""

    lambda_value: float = 1e4
    p_value: float = 0.001
    max_iterations: int = 10

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply AALS baseline correction."""
        y = chromatogram.intensity
        L = len(y)
        D = sparse.diags([1, -2, 1], [0, 1, 2], shape=(L-2, L))
        w = np.ones(L)
        z = np.ones(L)
        for i in range(self.max_iterations):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + self.lambda_value * D.dot(D.transpose())
            z = spsolve(Z, w * y)
            w = self.p_value * (y > z) + (1 - self.p_value) * (y <= z)

        return Chromatogram(
            time=chromatogram.time,
            intensity=chromatogram.intensity - z,
            metadata=chromatogram.metadata,
            peaks=chromatogram.peaks,
            baseline=z
        )

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate chromatogram can be processed."""
        if len(chromatogram.intensity) < 3:
            raise ValueError("Chromatogram too short for baseline correction")
