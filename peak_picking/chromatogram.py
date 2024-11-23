from dataclasses import dataclass, field
import numpy as np
from typing import List, Optional

from .peak import Peak
from .building_block import BuildingBlock

@dataclass
class Chromatogram:
    """Class to represent a chromatogram

    Attributes:
        x (Optional[np.ndarray]): time values of the chromatogram
        y (Optional[np.ndarray]): intensity values of the chromatogram
        y_corrected (Optional[np.ndarray]): intensity values of the chromatogram after baseline correction
        peaks (Optional[List[Peak]]): peaks found in the chromatogram
        picked_peak (Optional[Peak]): peak picked from the chromatogram
        building_blocks (Optional[List[BuildingBlock]]): building blocks of the compound the chromatogram belongs to

    Methods:
        _validate_chromatograms: Check if the chromatograms are of type Chromatogram
        _validate_peaks: Check if the peicked peak and the time of the picked peak of the chromatograms are not None
        __eq__: Check if two chromatograms are equal with respect to the time of their picked peaks
        __ne__: Check if two chromatograms are not equal with respect to the time of their picked peaks
        __lt__: Check if one chromatogram is less than another with respect to the time of their picked peaks
        __le__: Check if one chromatogram is less than or equal to another with respect to the time of their picked peaks
        __gt__: Check if one chromatogram is greater than another with respect to the time of their picked peaks
        __ge__: Check if one chromatogram is greater than or equal to another with respect to the time of their picked peaks
        __hash__: Return the hash value of the chromatogram
        __str__: Return the string representation of the chromatogram
        __repr__: Return the string representation of the chromatogram
    """
    x: Optional[np.array] = None
    y: Optional[np.array] = None
    y_corrected: Optional[np.array] = None
    peaks: List[Peak] = field(default_factory=list)
    picked_peak: Optional[Peak] = None
    building_blocks: Optional[List[BuildingBlock]] = None


    def _validate_chromatograms(self, other) -> bool:
        """Check if the chromatograms are of type Chromatogram

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the chromatograms are of type Chromatogram, False otherwise

        Raises:
            ValueError: If the chromatograms are not of type Chromatogram
        """
        if not isinstance(other, Chromatogram):
            try:
                raise ValueError("Cannot compare Chromatogram with non-Chromatogram object")
            except ValueError as e:
                print(f"Caught error: {e}")
                return False
        return True


    def _validate_peak_times(self, other) -> bool:
        """Check if the time of the picked peak of the chromatograms are not None

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the time of the picked peak of the chromatograms are not None, False otherwise

        Raises:
            ValueError: If the picked peak of either chromatogram is None
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if None in [self.picked_peak, other.picked_peak]:
            try:
                raise ValueError("Cannot compare Chromatogram with no picked peaks")
            except ValueError as e:
                print(f"Caught error: {e}")
                return False

        if None in [self.picked_peak.time, other.picked_peak.time]:
            try:
                raise ValueError("Cannot compare Chromatogram with no picked peak times")
            except ValueError as e:
                print(f"Caught error: {e}")
                return False

        return True


    def __eq__(self, other) -> bool:
        """Check if two chromatograms are equal with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the two chromatograms are equal with respect to the time of their picked peaks, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self.picked_peak.time == other.picked_peak.time
        return False


    def __ne__(self, other) -> bool:
        """Check if two chromatograms are not equal with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the two chromatograms are not equal with respect to the time of their picked peaks, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return not self.__eq__(other)
        return False


    def __lt__(self, other) -> bool:
        """Check if one chromatogram is less than the other with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the current chromatogram's picked peak time is less than the other chromatogram's picked peak time, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self.picked_peak.time < other.picked_peak.time
        return False


    def __le__(self, other) -> bool:
        """Check if one chromatogram is less than or equal to the other with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the current chromatogram's picked peak time is less than or equal to the other chromatogram's picked peak time, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self.picked_peak.time <= other.picked_peak.time
        return False


    def __gt__(self, other) -> bool:
        """Check if one chromatogram is greater than the other with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the current chromatogram's picked peak time is greater than the other chromatogram's picked peak time, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self.picked_peak.time > other.picked_peak.time
        return False


    def __ge__(self, other) -> bool:
        """Check if one chromatogram is greater than or equal to the other with respect to the time of their picked peaks

        Args:
            other (Chromatogram): Another chromatogram object to compare with

        Returns:
            bool: True if the current chromatogram's picked peak time is greater than or equal to the other chromatogram's picked peak time, False otherwise

        Raises:
            ValueError: If other is not a Chromatogram object
            ValueError: If the time of the picked peak of either chromatogram is None
        """
        if self._validate_chromatograms(other) and self._validate_peak_times(other):
            return self.picked_peak.time >= other.picked_peak.time
        return False

    def __hash__(self) -> int:
        """Return a hash of the chromatogram

        Args:
            None

        Returns:
            int: A hash of the chromatogram

        Raises:
            None
        """
        return hash(self.y)

    def __str__(self) -> str:
        """Return a string representation of the chromatogram

        Args:
            None

        Returns:
            str: A string representation of the chromatogram

        Raises:
            None
        """

        return f"Chromatogram with {len(self.peaks) if self.peaks is not None else 0} peaks and " + \
        f"picked peak at {self.picked_peak.time if self.picked_peak is not None else None}"


    def __repr__(self) -> str:
        """Return a string representation of the chromatogram

        Args:
            None

        Returns:
            str: A string representation of the chromatogram

        Raises:
            None
        """
        return self.__str__()
