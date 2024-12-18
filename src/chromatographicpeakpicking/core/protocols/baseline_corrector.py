from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar
import numpy as np

from . import Config
from core.chromatogram import Chromatogram

# Type variable for configuration, bound to IConfig
ConfigT = TypeVar('ConfigT', bound=Config)

@dataclass
class BaselineCorrector(ABC, Generic[ConfigT]):
    """Abstract base class for baseline correction algorithms.

    This class defines the interface for baseline correction algorithms.
    All baseline correctors should inherit from this class and implement
    the correct_baseline method.

    Attributes:
        config: Configuration object of type ConfigT (must inherit from IConfig)
            Contains algorithm-specific parameters

    Type Parameters:
        ConfigT: Configuration type that inherits from IConfig
    """
    config: ConfigT

    def validate_chromatogram(self, chrom: Chromatogram) -> None:
        """Validate chromatogram data before processing.

        Args:
            chrom: Chromatogram object to validate

        Raises:
            ValueError: If chromatogram data is invalid
            TypeError: If chromatogram is not the correct type
        """
        if not isinstance(chrom, Chromatogram):
            raise TypeError("Input must be a Chromatogram object")

        if chrom.y is None:
            raise ValueError("Chromatogram contains no signal data")

        if not isinstance(chrom.y, np.ndarray):
            raise ValueError("Chromatogram signal must be a numpy array")

        if len(chrom.y) == 0:
            raise ValueError("Chromatogram signal is empty")

        if not np.all(np.isfinite(chrom.y)):
            raise ValueError("Chromatogram signal contains NaN or infinite values")

    @abstractmethod
    def correct_baseline(self, chrom: Chromatogram) -> Chromatogram:
        """Abstract method for baseline correction.

        Implementations should:
            1. Apply baseline correction to the chromatogram signal
            2. Store the corrected signal in chrom.y_corrected
            3. Return the modified chromatogram object
            4. Handle any algorithm-specific errors

        Args:
            chrom: Chromatogram object containing the signal to be corrected

        Returns:
            Chromatogram with corrected baseline in y_corrected attribute

        Raises:
            NotImplementedError: If the method is not implemented
            ValueError: If input data is invalid
            TypeError: If input is not a Chromatogram object
        """
        raise NotImplementedError("Baseline correction method not implemented")

    def __call__(self, chrom: Chromatogram) -> Chromatogram:
        """Make the corrector callable.

        Provides a convenient way to apply baseline correction:
        corrector(chromatogram) instead of corrector.correct_baseline(chromatogram)

        Args:
            chrom: Chromatogram object to correct

        Returns:
            Corrected chromatogram
        """
        return self.correct_baseline(chrom)
