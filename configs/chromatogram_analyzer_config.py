from dataclasses import dataclass
from .Iconfig import IConfig

@dataclass
class ChromatogramAnalyzerConfig(IConfig):
    """Configuration for chromatogram analysis.
    Controls the behavior of signal analysis with parameters for:
        - Moving window calculations
        - Noise estimation
        - Minimal variation region detection
        - Quality thresholds
    """
    # Moving window parameters
    window_width: int = 15  # Width for moving calculations
    window_overlap: float = 0.5  # Fraction of window overlap
    min_window_points: int = 5  # Minimum points in a window

    # Noise estimation parameters
    variation_threshold: float = 1.5  # Factor above minimum std for quiet regions
    min_region_width: int = 5  # Minimum width of quiet regions
    max_region_gap: int = 20  # Maximum gap between regions to merge
    noise_percentile: float = 50.0  # Percentile for noise estimation

    # Quality thresholds
    min_regions_required: int = 3  # Minimum number of quiet regions
    max_noise_variance: float = 2.0  # Maximum allowed variance in noise estimates
    edge_exclusion: float = 0.05  # Fraction of edges to exclude

    # Baseline parameters
    baseline_percentile: float = 10.0  # Percentile for baseline estimation
    drift_window: int = 100  # Window for drift calculation

    # Distribution analysis
    smoothing_window: int = 5  # Window for distribution calculations
    outlier_threshold: float = 3.0  # Standard deviations for outlier detection
