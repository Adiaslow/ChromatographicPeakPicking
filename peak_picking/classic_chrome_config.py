from dataclasses import dataclass

from config import Config

@dataclass
class ClassicChromeConfig(Config):
    min_peak_height: float = 75
    min_peak_distance: int = 5
    peak_prominence_factor: float = 0.4
    minor_peak_height_factor: float = 0.5
    minor_peak_prominence_factor: float = 0.2
