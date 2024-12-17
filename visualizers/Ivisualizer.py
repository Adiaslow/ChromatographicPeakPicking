# External imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from matplotlib.figure import Figure
from typing import Generic, TypeVar

# Internal imports
from configs.Iconfig import IConfig
from core.chromatogram import Chromatogram
from visualizers.image_type import ImageType

ConfigT = TypeVar('ConfigT', bound='IConfig')


@dataclass
class IVisualizer(ABC, Generic[ConfigT]):
    """Abstract class to define the interface for visualizers.

    Attributes:
        config (ConfigT): Configuration object for the visualizer

    Methods:
        visualize: Abstract method to visualize chromatogram data with peaks and time annotations
        save: Save the figure to a file
        __call__: Call the visualize method
    """
    config: ConfigT


    @abstractmethod
    def visualize(
        self,
        chrom: Chromatogram
    ) -> Figure:
        """Abstract method to visualize chromatogram data with peaks and time annotations.

        Args:
            chrom: Chromatogram object to visualize

        Returns:
            Figure: The generated figure

        Raises:
            NotImplementedError: If the method is not implemented
        """
        raise NotImplementedError("Visualizer must implement visualize method")


    def save(
        self,
        fig: Figure,
        path: str,
        type: ImageType
    ) -> None:
        """Save the figure to a file

        Args:
            fig (Figure): figure to be saved
            path (str): path to save the figure
            type (ImageType): type of image to save

        Returns:
            None

        Raises:
            None
        """
        if type == ImageType.PNG or type not in [ImageType.SVG, ImageType.PDF]:
            fig.savefig(path, format='png')
        elif type == ImageType.SVG:
            fig.savefig(path, format='svg')
        else:
            fig.savefig(path, format='pdf')


    def __call__(
        self,
        chrom: Chromatogram
    ) -> Figure:
        """Call the visualize method

        Args:
            chrom: Chromatogram object to visualize

        Returns:
            Figure: The generated figure

        Raises:
            None
        """
        return self.visualize(chrom)
