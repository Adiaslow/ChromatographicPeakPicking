from dataclasses import dataclass

from configs.Iconfig import IConfig

@dataclass
class AALSConfig(IConfig):
    """Configuration for Adaptive Asymmetric Least Squares baseline correction.

    Attributes:
        lam (float): Smoothness parameter that controls the flexibility of the baseline.
            Higher values (e.g., 1e5) create smoother baselines, while lower values
            (e.g., 1e2) allow the baseline to follow the data more closely.
            Default: 1e2

        p (float): Asymmetry parameter that determines the balance between positive and
            negative residuals. Values between 0 and 0.5 penalize positive residuals
            more than negative ones. Smaller values (e.g., 0.001) create baselines that
            follow the lower envelope of the data more closely.
            Default: 0.1

        niter (int): Number of iterations for the iterative reweighting process.
            More iterations can improve baseline quality but increase computation time.
            Usually converges within 10-20 iterations.
            Default: 10
    """
    lam: float = 1e2
    p: float = 0.1
    niter: int = 10
