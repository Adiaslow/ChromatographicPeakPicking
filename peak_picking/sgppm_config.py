from dataclasses import dataclass

from .config import Config

@dataclass
class SGPPMConfig(Config):
    """Class for storing configuration parameters for the SGPPM algorithm.

    Attributes:
        correction_method (str): the method used for baseline correction
        window_length (int): the length of the window used for Savitzky-Golay filtering
        height_threshold (float): the threshold for peak height
        stddev_threshold (float): the threshold for standard deviation
        fit_points (int): the number of points used for fitting
        search_rel_height (float): the relative height used for searching
        pick_rel_height (float): the relative height used for picking

    Methods:
        None
    """
    correction_method = "SWM"
    window_length = 3
    height_threshold = 4380316.1070267465
    stddev_threshold = 1.164
    fit_points = 100
    search_rel_height = 0.001
    pick_rel_height = 0.3
