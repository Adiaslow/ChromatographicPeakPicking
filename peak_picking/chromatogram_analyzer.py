from dataclasses import dataclass
import numpy as np
from typing import Dict

from .chromatogram import Chromatogram

@dataclass
class ChromatogramAnalyzer:
    @staticmethod
    def analyze_chromatogram(chromatogram: Chromatogram) -> Dict:
        noise = ChromatogramAnalyzer._calculate_noise(chromatogram)
        snr = ChromatogramAnalyzer._calculate_snr(chromatogram, noise)
        baseline = ChromatogramAnalyzer._calculate_baseline(chromatogram)
        drift = ChromatogramAnalyzer._calculate_drift(chromatogram)
        return {
            'noise_level': noise,
            'signal_to_noise': snr,
            'baseline_mean': baseline,
            'baseline_drift': drift
        }

    @staticmethod
    def _calculate_noise(chromatogram: Chromatogram) -> float:
        noise_region = chromatogram.y[:int(len(chromatogram.y) * 0.1)]
        return np.std(noise_region)

    @staticmethod
    def _calculate_snr(chromatogram: Chromatogram, noise: float) -> float:
        signal = np.max(chromatogram.y) - np.min(chromatogram.y)
        return signal / noise if noise > 0 else float('inf')

    @staticmethod
    def _calculate_baseline(chromatogram: Chromatogram) -> float:
        return np.percentile(chromatogram.y, 10)

    @staticmethod
    def _calculate_drift(chromatogram: Chromatogram) -> float:
        return np.polyfit(chromatogram.x, chromatogram.y, 1)[0]
