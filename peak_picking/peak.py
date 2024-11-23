from dataclasses import dataclass
import numpy as np
from typing import List, Optional, Tuple, Union

@dataclass
class Peak:
    """Peak class to store peak information

    Attributes:
        time (Optional[float]): time of the peak
        index (Optional[int]): index of the peak
        height (Optional[float]): height of the peak
        width (Optional[float]): width of the peak
        left_base (Optional[float]): left base of the peak
        right_base (Optional[float]): right base of the peak
        area (Optional[float]): area of the peak
        symmetry (Optional[float]): symmetry of the peak
        skewness (Optional[float]): skewness of the peak
        score (Optional[float]): score of the peak
        approximation_curve (Optional[np.ndarray]): approximation curve of the peak

    Methods:
        _get_attributes(self) -> List[Union[float, int, np.ndarray, None]: Return the attributes of the peak
        __eq__(self, other) -> bool: Check if two peaks are equal with respect to time
        __ne__(self, other) -> bool: Check if two peaks are not equal with respect to time
        __lt__(self, other) -> bool: Check if one peak is less than the other with respect to time
        __le__(self, other) -> bool: Check if one peak is less than or equal to the other with respect to time
        __gt__(self, other) -> bool: Check if one peak is greater than the other with respect to time
        __ge__(self, other) -> bool: Check if one peak is greater than or equal to the other with respect to time
        __hash__(self) -> int: Return the hash value of the peak
        __str__(self) -> str: Return the string representation of the peak
        __repr__(self) -> str: Return the string representation of the peak
    """
    time: Optional[float] = np.NaN
    index: Optional[int] = np.NaN
    height: Optional[float] = np.NaN
    width: Optional[float] = np.NaN
    left_base: Optional[float] = np.NaN
    right_base: Optional[float] = np.NaN
    area: Optional[float] = np.NaN
    symmetry: Optional[float] = np.NaN
    skewness: Optional[float] = np.NaN
    score: Optional[float] = np.NaN
    approximation_curve: Optional[np.ndarray] = None


    def _get_attributes(self) -> List[Union[float, int, np.ndarray, None]]:
        """Return the attributes of the peak

        Args:
            None

        Returns:
            List[Union[float, int, np.ndarray, None]]: List of peak attributes

        Raises:
            None
        """
        return [
            self.time,
            self.index,
            self.height,
            self.width,
            self.left_base,
            self.right_base,
            self.area,
            self.symmetry,
            self.skewness,
            self.score,
            self.approximation_curve
        ]


    def __eq__(self, other) -> bool:
        """Check if two peaks are equal with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the two peaks are equal with respect to time, False otherwise

        Raises:
            ValueError: If other is not a Peak object
            ValueError: If the time of either peak is None or if the time of the other peak is None
        """
        if not isinstance(other, Peak):
            raise ValueError("Cannot compare Peak with non-Peak object")
        if self.time is None or other.time is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.time == other.time


    def __ne__(self, other) -> bool:
        """Check if two peaks are not equal with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the two peaks are not equal with respect to time, False otherwise

        Raises:
            None
        """
        return not self.__eq__(other)


    def __lt__(self, other) -> bool:
        """Check if one peak is less than the other with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the current peak is less than the other peak with respect to time, False otherwise

        Raises:
            ValueError: If other is not a Peak object
            ValueError: If the time of either peak is None or if the time of the other peak is None
        """
        if not isinstance(other, Peak):
            raise ValueError("Cannot compare Peak with non-Peak object")
        if self.time is None or other.time is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.time < other.time


    def __le__(self, other: object) -> bool:
        """Check if one peak is less than or equal to the other with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the current peak is less than or equal to the other peak with respect to time, False otherwise

        Raises:
            ValueError: If other is not a Peak object
            ValueError: If the time of either peak is None or if the time of the other peak is None
        """
        if not isinstance(other, Peak):
            raise ValueError("Cannot compare Peak with non-Peak object")
        if self.time is None or other.time is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.time <= other.time


    def __gt__(self, other: object) -> bool:
        """Check if one peak is greater than the other with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the current peak is greater than the other peak with respect to time, False otherwise

        Raises:
            ValueError: If other is not a Peak object
            ValueError: If the time of either peak is None or if the time of the other peak is None
        """
        if not isinstance(other, Peak):
            raise ValueError("Cannot compare Peak with non-Peak object")
        if self.time is None or other.time is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.time > other.time


    def __ge__(self, other: object) -> bool:
        """Check if one peak is greater than or equal to the other with respect to time

        Args:
            other (Peak): Another peak object to compare with

        Returns:
            bool: True if the current peak is greater than or equal to the other peak with respect to time, False otherwise

        Raises:
            ValueError: If other is not a Peak object
            ValueError: If the time of either peak is None or if the time of the other peak is None
        """
        if not isinstance(other, Peak):
            raise ValueError("Cannot compare Peak with non-Peak object")
        if self.time is None or other.time is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.time >= other.time


    def __hash__(self) -> int:
        """Return the hash value of the peak

        Args:
            None

        Returns:
            int: Hash value of the peak

        Raises:
            ValueError: If all attributes of the peak are None
        """
        if self._get_attributes() == [None] * len(self._get_attributes()):
            raise ValueError("Cannot hash peak with all None values")
        return hash((
            self.time,
            self.index,
            self.height,
            self.width,
            self.left_base,
            self.right_base,
            self.area,
            self.symmetry,
            self.skewness,
            self.score))


    def __str__(self) -> str:
        """Return the string representation of the peak

        Args:
            None

        Returns:
            str: String representation of the peak

        Raises:
            ValueError: If all attributes of the peak are None
        """
        if self._get_attributes() == [None] * len(self._get_attributes()):
            raise ValueError("Cannot hash peak with all None values")

        return f"Peak with time {self.time}" + \
        f"index {self.index}" + \
        f"height {self.height}" + \
        f"width {self.width}" + \
        f"left_base {self.left_base}" + \
        f"right_base {self.right_base}" + \
        f"area {self.area}" + \
        f"symmetry {self.symmetry}" + \
        f"skewness {self.skewness}" + \
        f"score {self.score}"


    def __repr__(self) -> str:
        """Return the string representation of the peak

        Args:
            None

        Returns:
            str: String representation of the peak

        Raises:
            None
        """
        return self.__str__()
