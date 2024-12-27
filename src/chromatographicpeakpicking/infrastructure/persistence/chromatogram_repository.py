# src/chromatographicpeakpicking/infrastructure/persistence/chromatogram_repository.py
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from .base_repository import BaseRepository
from ...core.domain.chromatogram import Chromatogram

class ChromatogramRepository(BaseRepository[Chromatogram]):
    """Repository for chromatogram data."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save(self, chromatogram: Chromatogram) -> None:
        """Save a chromatogram to storage."""
        data = chromatogram.to_dict()
        path = self.storage_path / f"{chromatogram.id}.json"
        with open(path, 'w') as f:
            json.dump(data, f)

    def get(self, id: str) -> Optional[Chromatogram]:
        """Get a chromatogram by ID."""
        path = self.storage_path / f"{id}.json"
        if not path.exists():
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        return Chromatogram.from_dict(data)

    def get_all(self) -> List[Chromatogram]:
        """Get all chromatograms."""
        chromatograms = []
        for path in self.storage_path.glob("*.json"):
            with open(path, 'r') as f:
                data = json.load(f)
            chromatograms.append(Chromatogram.from_dict(data))
        return chromatograms

    def delete(self, id: str) -> None:
        """Delete a chromatogram."""
        path = self.storage_path / f"{id}.json"
        if path.exists():
            path.unlink()
