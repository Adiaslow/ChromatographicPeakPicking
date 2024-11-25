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
    fit_points = 100
    search_rel_height = 0.01  # Increased to focus on major peaks
    pick_rel_height = 0.4  # Adjusted for better peak selection
    gaussian_residuals_threshold = 3.0  # More lenient fit requirements
    height_threshold = 5.0  # Lowered minimum height
    stddev_threshold = 1.5  # Slightly more lenient
    width_min = 0.15  # More flexible width range
    width_max = 1.2
    min_distance_factor = 0.03  # Allow closer peaks
    symmetry_threshold = 0.25  # More lenient symmetry
    noise_factor = 3.0  # Reduced noise threshold
