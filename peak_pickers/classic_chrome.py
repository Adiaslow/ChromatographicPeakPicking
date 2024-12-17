# External imports
from dataclasses import dataclass
import networkx as nx
import numpy as np
from scipy.signal import find_peaks
from typing import List, Union

# Internal imports
from analyzers.peak_analyzer import PeakAnalyzer
from baseline_correctors.aals import AALS
from configs.classic_chrome_config import ClassicChromeConfig
from core.chromatogram import Chromatogram
from core.peak import Peak
from peak_pickers.Ipeak_picker import IPeakPicker


@dataclass
class ClassicChrome(
    IPeakPicker[ClassicChromeConfig]
):
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


    def pick_peaks(
        self,
        chromatograms: Union[List[Chromatogram],
            Chromatogram]
    ) -> Union[List[Chromatogram], Chromatogram]:
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
        elif chromatograms is not List[Chromatogram]:
            raise ValueError("Input must be a Chromatogram or a list of Chromatograms")

        chromatograms = self._prepare_chromatograms(chromatograms)
        chromatograms = self._find_peaks(chromatograms)
        chromatograms = self._select_peaks(chromatograms)

        return chromatograms[0] if len(chromatograms) == 1 else chromatograms


    def _prepare_chromatograms(
        self,
        chromatograms: List[Chromatogram],
        method="ALSS"
    ) -> List[Chromatogram]:
        """Prepare chromatograms for peak picking.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be prepared

        Returns:
            List[Chromatogram]: chromatograms prepared for peak picking

        Raises:
            None
        """
        for chrom in chromatograms:
            chrom.y_corrected = AALS(chrom)
        return chromatograms


    def _find_peaks(
        self,
        chromatograms: List[Chromatogram]
    ) -> List[Chromatogram]:
        """Find peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks found

        Raises:
            None
        """
        for chrom in chromatograms:
            peaks = find_peaks(
                chrom.y_corrected,
                height=self.config.min_peak_height,
                distance=self.config.min_peak_distance,
                prominence=self.config.peak_prominence_factor
                * np.max(chrom.y_corrected)
            )[0]
            for peak in peaks:
                _peak = Peak()
                _peak['time'] = chrom.x[int(peak)] if chrom.x is not None else np.NaN
                _peak['index'] = int(peak)
                _peak['height'] = chrom.y_corrected[int(peak)] if chrom.y_corrected is not None else np.NaN
                _peak = PeakAnalyzer.analyze_peak(_peak, chrom)
                chrom.peaks.append(_peak)
        return chromatograms


    def _select_peaks(
        self,
        chromatograms: List[Chromatogram]
    ) -> List[Chromatogram]:
        """Select peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks selected

        Raises:
            None
        """
        return chromatograms


    def _build_hierarchy(
        self,
        chromatograms: List[Chromatogram]
    ) -> nx.DiGraph:
        """Build hierarchy of peaks in chromatograms.

        Args:
            chromatograms (List[Chromatogram]): chromatograms to be analyzed

        Returns:
            List[Chromatogram]: chromatograms with peaks hierarchically organized

        Raises:
            None
        """
        return nx.DiGraph()
