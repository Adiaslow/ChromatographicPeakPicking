# src/chromatographicpeakpicking/analysis/baseline/aals.py
"""
A module for implementing the Asymmetric Least Squares (AALS) baseline correction algorithm.
"""

from dataclasses import dataclass, field
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from src.chromatographicpeakpicking.core.protocols.configurable import Configurable
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig,
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.domain.chromatogram import Chromatogram

@dataclass
class AALSConfig(BaseConfig):
    """
    Configuration for the AALS baseline correction.
    """
    def __init__(self, lambda_value: float = 1e4, p_value: float = 0.001, max_iterations: int = 10):
        super().__init__(metadata=ConfigMetadata(
            name="AALSConfig",
            version="1.0",
            description="Configuration for AALS Baseline Corrector",
            defaults={"lambda_value": 1e2, "p_value": 0.001, "max_iterations": 10},
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={
            "lambda_value": lambda_value,
            "p_value": p_value,
            "max_iterations": max_iterations
            }
        )

@dataclass
class AALSCorrector(Configurable[AALSConfig]):
    """
    A class for applying the Asymmetric Least Squares (AALS) baseline correction algorithm.
    """
    config: AALSConfig = field(default_factory=AALSConfig)

    def configure(self, config: AALSConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def get_metadata(self) -> ConfigMetadata:
        return self.config.metadata

    def validate_config(self, config: AALSConfig) -> ValidationResult:
        errors = []
        if config.parameters["lambda_value"] <= 0:
            errors.append("Lambda value must be greater than 0.")
        if config.parameters["p_value"] <= 0 or config.parameters["p_value"] >= 1:
            errors.append("P value must be between 0 and 1.")
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply AALS baseline correction."""
        y = chromatogram.intensity
        length = len(y)
        diff_matrix = sparse.diags([1, -2, 1], [0, 1, 2], shape=(length, length)) # type: ignore
        weights = np.ones(length)
        baseline = np.ones(length)
        for _ in range(self.config.parameters["max_iterations"]):
            weight_matrix = sparse.spdiags(weights, 0, length, length)
            z_matrix = weight_matrix + \
            self.config.parameters["lambda_value"] * \
            diff_matrix.T.dot(diff_matrix)
            baseline = spsolve(z_matrix, weights * y)
            weights = self.config.parameters["p_value"] * \
            (y > baseline) + (1 - self.config.parameters["p_value"]) * \
            (y <= baseline)

        return Chromatogram(
            time=chromatogram.time,
            intensity=chromatogram.intensity - baseline,
            metadata=chromatogram.metadata,
            peaks=chromatogram.peaks,
            baseline=baseline
        )

    def validate(self, chromatogram: Chromatogram) -> None:
        """Validate chromatogram can be processed."""
        if len(chromatogram.intensity) < 3:
            raise ValueError("Chromatogram too short for baseline correction")
