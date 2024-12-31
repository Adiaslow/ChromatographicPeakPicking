# External imports
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

# Internal imports
from configs.chromatogram_visualizer_config import ChromatogramVisualizerConfig
from core.chromatogram import Chromatogram
from visualizers.Ivisualizer import IVisualizer


@dataclass
class ChromatogramVisualizer(
    IVisualizer
):
    """Visualizer for chromatogram data.

    Attributes:
        config (ChromatogramVisualizerConfig): Configuration for the visualizer

    Methods:
        visualize: Generate a visualization of a chromatogram
        save: Save a figure to a file
    """
    config: ChromatogramVisualizerConfig = field(default_factory=ChromatogramVisualizerConfig)

    def visualize(
        self,
        chrom: Chromatogram
    ) -> Figure:
        """Visualize chromatogram data with peaks and time annotations.
        Args:
            chrom: Chromatogram object to visualize

        Returns:
            matplotlib.figure.Figure: The generated figure

        Raises:
            None
        """
        # Apply style configuration
        plt.rcParams.update(self.config.rcParamas)
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        # Plot base chromatogram
        ax.plot(
            chrom.x,
            chrom.y,
            color='tab:blue',
            label='Signal',
            alpha=0.7
        )
        # Plot all detected peaks and add annotations
        if chrom.peaks:
            peak_times = []
            peak_heights = []
            for peak in chrom.peaks:
                peak_times.append(peak['time'])
                peak_heights.append(peak['height'])

                # Add shaded area under the peak
                peak_slice = slice(peak['left_base_index'], peak['right_base_index'] + 1)
                ax.fill_between(
                    chrom.x[peak_slice],
                    chrom.y[peak_slice],
                    alpha=0.3,
                    hatch='///',
                    color='tab:orange' if peak is not chrom.picked_peak else 'tab:green'
                )

                # Plot peak without label to avoid legend duplication
                ax.plot(
                    peak['time'],
                    peak['height'],
                    color='tab:orange',
                    marker='.',
                    markersize=8,
                    zorder=5
                )
                if peak is chrom.picked_peak:
                    continue
                # Add annotation for each peak
                ax.annotate(
                    f'{peak["time"]:.1f}\nArea: {peak["area"]:.1f}',
                    xy=(peak['time'], peak['height']),
                    xytext=(0, 20),
                    textcoords='offset points',
                    ha='center',
                    va='top',
                    fontsize=10,
                    color='tab:orange'
                )
            # Add a single legend entry for all detected peaks
            ax.scatter(
                [],
                [],
                color='tab:orange',
                label='Detected Peaks'
            )

        # Highlight picked peak
        if chrom.picked_peak is not None:
            ax.scatter(
                chrom.picked_peak['time'],
                chrom.picked_peak['height'],
                color='tab:green',
                marker='.',
                s=200,
                label='Picked Peak'
            )
            # Add vertical line at picked peak
            ax.axvline(
                x=chrom.picked_peak['time'],
                color='tab:green',
                linestyle='--',
                alpha=0.5,
                linewidth=1
            )
            # Add special annotation for picked peak
            ax.annotate(
                f'{chrom.picked_peak["time"]:.1f}\nArea: {chrom.picked_peak["area"]:.1f}',
                xy=(chrom.picked_peak['time'], chrom.picked_peak['height']),
                xytext=(0, 20),
                textcoords='offset points',
                ha='center',
                va='top',
                fontsize=10,
                color='tab:green',
                weight='bold'
            )
        # Set title with building block information
        bb_names = [
            bb.name for bb in chrom.building_blocks if bb is not None
        ] if chrom.building_blocks is not None else None
        ax.set_title(
            f"Chromatogram: {'_'.join(bb_names[::-1])}") \
                if bb_names is not None \
                else ax.set_title("Chromatogram: Unknown Compound"
                )
        # Set labels and grid
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Intensity")
        ax.grid(True, alpha=0.3)
        # Set x limits if we have data
        if chrom.x is not None:
            ax.set_xlim([chrom.x[0], chrom.x[-1]])
        # Set y limits: 0 to nearest hundred above max
        if chrom.y is not None:
            max_y = np.max(chrom.y)
            upper_limit = np.ceil(max_y / 100) * 100
            # Add extra space for annotations
            ax.set_ylim([0, upper_limit * 1.1])
        # Add legend if we have any labeled elements
        if ax.get_legend_handles_labels()[0]:
            ax.legend()
        # Adjust layout to prevent label clipping
        fig.tight_layout()
        return fig
