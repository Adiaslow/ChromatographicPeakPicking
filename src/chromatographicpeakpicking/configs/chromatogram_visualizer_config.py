from dataclasses import dataclass
import matplotlib.pyplot as plt
from configs.Iconfig import IConfig

@dataclass
class ChromatogramVisualizerConfig(
    IConfig
):
    """Configuration for chromatogram visualizer.

    Attributes:
        rcParamas (dict): Matplotlib rcParams for visual

    Methods:
        None
    """
    def __post_init__(
        self
    ):
        """Initialize default rcParams.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.rcParamas = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial'] + \
            (plt.rcParams['font.sans-serif'] or []),
        'font.size': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 10,
        'figure.dpi': 100,
        'axes.linewidth': 3,
        'xtick.major.width': 3,
        'ytick.major.width': 3,
        'xtick.major.size': 8,
        'ytick.major.size': 8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'font.weight': 'bold',
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'lines.linewidth': 2,
    }
