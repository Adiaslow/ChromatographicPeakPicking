# src/chromatographicpeakpicking/infrastructure/persistence/peak_repository.py
from typing import Optional, List, Dict
from ...core.domain.peak import Peak
from .base_repository import BaseRepository
from ..logging.analysis_logger import AnalysisLogger

class PeakRepository(BaseRepository[Peak]):
    """Repository for managing Peak domain objects with proper persistence."""

    def __init__(self, logger: Optional[AnalysisLogger] = None):
        self._peaks: Dict[str, Peak] = {}
        self._logger = logger

    async def save(self, peak: Peak) -> None:
        """Save a peak to the repository.

        Args:
            peak: The Peak domain object to save
        """
        if not peak.id:
            raise ValueError("Peak must have an ID")

        self._peaks[peak.id] = peak
        if self._logger:
            self._logger.log_analysis_step(f"Saved peak {peak.id}")

    async def get(self, id: str) -> Optional[Peak]:
        """Retrieve a peak by ID.

        Args:
            id: The unique identifier of the peak

        Returns:
            The Peak if found, None otherwise
        """
        peak = self._peaks.get(id)
        if self._logger and peak:
            self._logger.log_analysis_step(f"Retrieved peak {id}")
        return peak

    async def get_all(self) -> List[Peak]:
        """Retrieve all peaks in the repository.

        Returns:
            List of all Peak objects
        """
        if self._logger:
            self._logger.log_analysis_step("Retrieved all peaks")
        return list(self._peaks.values())

    async def delete(self, id: str) -> None:
        """Delete a peak from the repository.

        Args:
            id: The unique identifier of the peak to delete
        """
        if id in self._peaks:
            del self._peaks[id]
            if self._logger:
                self._logger.log_analysis_step(f"Deleted peak {id}")
