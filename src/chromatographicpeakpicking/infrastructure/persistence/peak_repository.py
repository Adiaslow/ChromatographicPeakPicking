# src/chromatographicpeakpicking/infrastructure/persistence/peak_repository.py

"""
Repository for handling peak persistence.
"""

from .base_repository import BaseRepository

class PeakRepository(BaseRepository):
    def __init__(self):
        self.peaks = {}

    def save(self, peak):
        """
        Save a peak to the repository.

        Args:
            peak: The peak to save.
        """
        self.peaks[peak.id] = peak

    def get(self, peak_id):
        """
        Retrieve a peak by its ID.

        Args:
            peak_id: The ID of the peak to retrieve.
        """
        return self.peaks.get(peak_id)

    def get_all(self):
        """
        Retrieve all peaks from the repository.
        """
        return list(self.peaks.values())

    def delete(self, peak_id):
        """
        Delete a peak by its ID.

        Args:
            peak_id: The ID of the peak to delete.
        """
        if peak_id in self.peaks:
            del self.peaks[peak_id]
