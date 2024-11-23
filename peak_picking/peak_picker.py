from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, List, TypeVar, Union

from chromatogram import Chromatogram
from config import Config
from peak import Peak

ConfigT = TypeVar('ConfigT', bound='Config')

@dataclass
class PeakPicker(Generic[ConfigT]):
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
    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]]:
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
    def _prepare_chromatograms(self, chromatograms: List[Chromatogram], method: str) -> List[Chromatogram]:
        """Abstract method for preparing chromatograms for peak picking

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be prepared

        Returns:
            List[Chromatogram]: chromatograms prepared for peak picking

        Raises:
            None
        """
        pass


    @abstractmethod
    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Abstract method for finding peaks in chromatograms

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found

        Raises:
            None
        """
        pass


    @abstractmethod
    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Abstract method for selecting peaks in chromatograms

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks selected

        Raises:
            None
        """
        pass
