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
    window_length = 5
    fit_points = 100
    search_rel_height = 0.2
    pick_rel_height = 0.3
    gaussian_residuals_threshold = 6000.0
    height_threshold = 10.0
    stddev_threshold = 1.5
    width_min = 0.02
    width_max = 0.2
    min_distance_factor = 0.03
    symmetry_threshold = 0.25
    noise_factor = 3.0
