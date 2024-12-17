from dataclasses import dataclass

from .Iconfig import IConfig

@dataclass
class ClassicChromeConfig(IConfig):
    """Configuration for the Classic Chrome peak picking algorithm."""
    min_peak_height: float = 75
    min_peak_distance: int = 5
    peak_prominence_factor: float = 0.4
    minor_peak_height_factor: float = 0.5
    minor_peak_prominence_factor: float = 0.2
