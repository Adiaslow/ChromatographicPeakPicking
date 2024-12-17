# External imports
from enum import Enum


class ImageType(Enum):
    """Enum class for image types

    Attributes:
        PDF (str): PDF image type
        PNG (str): PNG image type
        SVG (str): SVG image type

    Methods:
        None
    """
    PDF = 'pdf'
    PNG = 'png'
    SVG = 'svg'
