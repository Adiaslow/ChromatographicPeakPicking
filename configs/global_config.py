# Internal imports
from configs.Iconfig import IConfig

class GlobalConfig(IConfig):
    """Global configuration for the peak picking pipeline.

    This configuration object contains global parameters for the peak picking
    pipeline. These parameters are used by all peak picking algorithms.

    Attributes:
        min_peak_height: Minimum peak height for peak picking
        min_peak_distance: Minimum peak distance for peak picking
        min_peak_width: Minimum peak width for peak picking
    """
    debug = False
