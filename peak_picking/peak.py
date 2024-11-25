from dataclasses import dataclass, field
import numpy as np
from typing import Dict

@dataclass
class Peak:
    """Peak class to store peak information

    Attributes:
        peak_metrics (Dict): dictionary to store peak metrics

    Methods:
        __eq__(self, other) -> bool: Check if two peaks are equal with respect to time
        __ne__(self, other) -> bool: Check if two peaks are not equal with respect to time
        __lt__(self, other) -> bool: Check if one peak is less than the other with respect to time
        __le__(self, other) -> bool: Check if one peak is less than or equal to the other with respect to time
        __gt__(self, other) -> bool: Check if one peak is greater than the other with respect to time
        __ge__(self, other) -> bool: Check if one peak is greater than or equal to the other with respect to time
        __hash__(self) -> int: Return the hash value of the peak
        __str__(self) -> str: Return the string representation of the peak
        __repr__(self) -> str: Return the string representation of the peak
        _validate_peak_metrics(self) -> bool: Check if at least one peak metric is not None or NaN
    """

    peak_metrics: Dict = field(default_factory=lambda: {
        'time': np.NaN,
        'index': np.NaN,
        'height': np.NaN,
        'width': np.NaN,
        'width_5': np.NaN,
        'left_base_time': np.NaN,
        'right_base_time': np.NaN,
        'left_base_index': np.NaN,
        'right_base_index': np.NaN,
        'area': np.NaN,
        'symmetry': np.NaN,
        'skewness': np.NaN,
        'prominence': np.NaN,
        'resolution': np.NaN,
        'gaussian_residuals': None,
        'score': np.NaN,
        'approximation_curve': None,
    })


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
        if self.peak_metrics['time'] is None or self.peak_metrics['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.peak_metrics['time'] == self.peak_metrics['time']


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
        if self.peak_metrics['time'] is None or self.peak_metrics['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.peak_metrics['time'] < self.peak_metrics['time']


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
        if self.peak_metrics['time'] is None or self.peak_metrics['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.peak_metrics['time'] <= self.peak_metrics['time']


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
        if self.peak_metrics['time'] is None or self.peak_metrics['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.peak_metrics['time'] > self.peak_metrics['time']


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
        if self.peak_metrics['time'] is None or self.peak_metrics['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self.peak_metrics['time'] >= self.peak_metrics['time']


    def __hash__(self) -> int:
        """Return the hash value of the peak

        Args:
            None

        Returns:
            int: Hash value of the peak

        Raises:
            ValueError: If all attributes of the peak are None
        """
        # If all peak_metrics aer np.NaN or Non, raise an error
        if not self._validate_peak_metrics():
            raise ValueError("Cannot hash peak with all None and NaN values")
        return hash(
            (
                self.peak_metrics.values()
            )
        )


    def __str__(self) -> str:
        """Return the string representation of the peak

        Args:
            None

        Returns:
            str: String representation of the peak

        Raises:
            ValueError: If all attributes of the peak are None
        """
        if not self._validate_peak_metrics():
            raise ValueError("Cannot print peak with all None and NaN values")

        _str = "Peak with "
        for key, value in self.peak_metrics.items():
            if key == 'approximation_curve':
                continue
            _temp_str = f"    {key}: {value},\n"
            _str += _temp_str

        return _str


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


    def _validate_peak_metrics(self) -> bool:
            for key, val in self.peak_metrics.items():
                if val is not None and not np.isnan(val):
                    return True
            return False
