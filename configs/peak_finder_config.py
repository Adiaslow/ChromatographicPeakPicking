from dataclasses import dataclass
from .Iconfig import IConfig

@dataclass
class PeakFinderConfig(IConfig):
    """Configuration for initial peak finding.

    Controls the behavior of peak detection with parameters for:
        - SNR thresholds
        - Prominence thresholds
        - Width calculations
        - Peak separation
        - Window lengths
    """
    # SNR and height parameters
    min_snr_factor: float = 3.0
    max_snr_factor: float = 10.0
    snr_scale: float = 0.1

    # Prominence parameters
    min_prominence_ratio: float = 0.01
    noise_prominence_factor: float = 2.0

    # Width parameters
    min_roughness_factor: float = 2.0
    max_roughness_factor: float = 10.0
    roughness_scale: float = 5.0

    # Peak separation
    peak_separation_factor: float = 1.5

    # Window length parameters
    min_window_points: int = 50
    min_window_roughness_factor: float = 5.0
    max_window_roughness_factor: float = 20.0
    window_roughness_scale: float = 10.0

    # Peak base detection
    relative_height: float = 0.3
