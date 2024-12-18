from dataclasses import dataclass, field
import numpy as np

from metrics.peak_metrics import PeakMetrics

@dataclass
class Peak:
    """Peak class to store peak information

    Attributes:
        peak_metrics (Dict): dictionary to store peak metrics

    Methods:
        _validate_peak_metrics(self) -> bool: Check if at least one peak metric is not None or NaN

        __getitem__(self, key: str) -> float: Allow dictionary-like access to metrics
        __setitem__(self, key: str, value: float) -> None: Allow dictionary-like setting of metrics

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

    metrics: PeakMetrics = field(default_factory=PeakMetrics)


    def _validate_peak_metrics(self) -> bool:
        return any(
            val is not None and not np.ma.is_masked(np.ma.masked_invalid(val))
            for key, val in self.metrics.get_all_metrics()
        )


    def __getitem__(self, key: str) -> float:
            """Allow dictionary-like access to metrics.

            Args:
                key: Name of the metric to retrieve

            Returns:
                Value of the requested metric

            Raises:
                KeyError: If metric name doesn't exist
            """
            value = self.metrics.get_metric(key)
            if value is None:
                raise KeyError(f"Metric '{key}' not found")
            return value


    def __setitem__(self, key: str, value: float) -> None:
        """Allow dictionary-like setting of metrics.

        Args:
            key: Name of the metric to set
            value: Value to set for the metric
        """
        self.metrics.set_metric(key, value)


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
        if self['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self['time'] == self['time']


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
        if self['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self['time'] < self['time']


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
        if self['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self['time'] <= self['time']


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
        if self['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self['time'] > self['time']


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
        if self['time'] is None:
            raise ValueError("Cannot compare Peaks with None time")
        return self['time'] >= self['time']


    def __hash__(self) -> int:
        if not self._validate_peak_metrics():
            raise ValueError("Cannot hash peak with all None and NaN values")
        return hash(tuple(self.metrics.get_all_metrics()))

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

        _str = "Peak with\n"
        metrics_dict = self.metrics.get_all_metrics()
        for key, value in metrics_dict.items():
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
