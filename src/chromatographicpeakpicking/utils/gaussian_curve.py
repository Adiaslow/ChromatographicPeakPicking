import numpy as np

@staticmethod
def gaussian_curve(
    y: np.ndarray,
    amplitude: float,
    mean: float,
    stddev: float
) -> np.ndarray:
    """Calculates the Gaussian curve.

    Args:
        y (np.ndarray): intensity values of the chromatogram
        amplitude (float): amplitude of the Gaussian curve
        mean (float): mean of the Gaussian curve
        stddev (float): standard deviation of the Gaussian curve

    Returns:
        np.ndarray: Gaussian curve

    Raises:
        None
    """
    return amplitude * np.exp(-((y - mean) ** 2) / (2 * stddev ** 2))
