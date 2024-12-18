from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, TypeVar, Union

from core.chromatogram import Chromatogram
from configs.Iconfig import IConfig

ConfigT = TypeVar('ConfigT', bound='IConfig')

@dataclass
class IPeakPicker(ABC, Generic[ConfigT]):
    """Abstract class for peak picking algorithms

    Attributes:
        None

    Methods:
        pick_peaks: Picks peaks in chromatograms
        _prepare_chromatograms: Prepares chromatograms for peak picking
        _find_peaks: Finds peaks in chromatograms
        _select_peaks: Selects peaks in chromatograms
    """
    config: ConfigT


    @abstractmethod
    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]:
        """Abstract method for picking peaks in chromatograms

        Args:
            chromatograms (Union[List[Chromatogram], Chromatogram]): chromatograms to be analyzed

        Returns:
            Union[List[Chromatogram], Chromatogram]: chromatograms with peaks found and selected

        Raises:
            None
        """
        pass

    @abstractmethod
    def _select_peak(self, chrom: Chromatogram) -> Chromatogram:
        """Abstract method for selecting peaks in chromatograms

        Args:
            chrom (Chromatogram): chromatogram to be analyzed

        Returns:
            Chromatogram: chromatogram with peaks selected

        Raises:
            None
        """
        pass
