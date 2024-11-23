from dataclasses import dataclass
import networkx as nx
import numpy as np
from scipy.signal import find_peaks
from typing import List, Union

from baseline_corrector import BaselineCorrector
from chromatogram import Chromatogram
from classic_chrome_config import ClassicChromeConfig
from peak import Peak
from peak_analyzer import PeakAnalyzer
from peak_picker import PeakPicker

@dataclass
class ClassicChrome(PeakPicker[ClassicChromeConfig]):
    """Classic Chrome peak picking algorithm.

    Attributes:
        config (ClassicChromeConfig): configuration for the Classic Chrome algorithm

    Methods:
        pick_peaks: Picks peaks in chromatograms
        _prepare_chromatograms: Prepares chromatograms for peak picking
        _find_peaks: Finds peaks in chromatograms
        _select_peaks: Selects peaks in chromatograms
    """
    config: ClassicChromeConfig = ClassicChromeConfig()


    def pick_peaks(self, chromatograms: Union[List[Chromatogram], Chromatogram]) -> Union[List[Chromatogram], Chromatogram]]:
        """Pick peaks in chromatograms.

        Args:
            chromatograms (Union[List[Chromatogram], Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found and selected

        Raises:
            ValueError: if input is not a Chromatogram or a list of Chromatograms

        """
        if chromatograms is Chromatogram:
            chromatograms = [chromatograms]
        elif chromatograms is List[Chromatogram]:
            pass
        else:
            raise ValueError("Input must be a Chromatogram or a list of Chromatograms")

        chromatograms = self._prepare_chromatograms(chromatograms)
        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        if len(chromatograms) == 1:
            return chromatograms[0]
        return chromatograms


    def _prepare_chromatograms(self, chromatograms: List[Chromatogram], method="ALSS") -> List[Chromatogram]:
        """Prepare chromatograms for peak picking.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be prepared

        Returns:
            List[Chromatogram]: chromatograms prepared for peak picking

        Raises:
            None
        """
        for chromatogram in chromatograms:
            chromatogram.y_corrected = BaselineCorrector.correct_baseline(y=chromatogram.y, method=method)
        return chromatograms


    def _find_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Find peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found

        Raises:
            None
        """
        for chromatogram in chromatograms:
            peaks = find_peaks(
                chromatogram.y_corrected,
                height=self.config.min_peak_height,
                distance=self.config.min_peak_distance,
                prominence=self.config.peak_prominence_factor
                * np.max(chromatogram.y_corrected)
            )[0]
            for peak in peaks:
                _peak = Peak(
                        time=chromatogram.x[int(peak)] if chromatogram.x is not None else np.NaN,
                        index=int(peak),
                        height=chromatogram.y_corrected[int(peak)] if chromatogram.y_corrected is not None else np.NaN
                    )
                _peak = PeakAnalyzer.analyze_peak(_peak, chromatogram)
                chromatogram.peaks.append(_peak)
        return chromatograms


    def _select_peaks(self, chromatograms: List[Chromatogram]) -> List[Chromatogram]:
        """Select peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks selected

        Raises:
            None
        """
        for chromatogram in chromatograms:
            for peak in chromatogram.peaks:
                pass
        return chromatograms


    def _build_hierarchy(self, chromatograms: List[Chromatogram]) -> nx.DiGraph:
        """Build hierarchy of peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks hierarchically organized

        Raises:
            None
        """
        G = nx.DiGraph()

        return G
