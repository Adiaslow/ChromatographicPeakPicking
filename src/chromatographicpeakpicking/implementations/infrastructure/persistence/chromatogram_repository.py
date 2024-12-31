# src/chromatographicpeakpicking/infrastructure/persistence/chromatogram_repository.py

"""
Repository for handling chromatogram persistence.
"""

from .base_repository import BaseRepository

class ChromatogramRepository(BaseRepository):
    def __init__(self):
        self.chromatograms = {}

    def save(self, chromatogram):
        """
        Save a chromatogram to the repository.

        Args:
            chromatogram: The chromatogram to save.
        """
        self.chromatograms[chromatogram.id] = chromatogram

    def get(self, chromatogram_id):
        """
        Retrieve a chromatogram by its ID.

        Args:
            chromatogram_id: The ID of the chromatogram to retrieve.
        """
        return self.chromatograms.get(chromatogram_id)

    def get_all(self):
        """
        Retrieve all chromatograms from the repository.
        """
        return list(self.chromatograms.values())

    def delete(self, chromatogram_id):
        """
        Delete a chromatogram by its ID.

        Args:
            chromatogram_id: The ID of the chromatogram to delete.
        """
        if chromatogram_id in self.chromatograms:
            del self.chromatograms[chromatogram_id]
