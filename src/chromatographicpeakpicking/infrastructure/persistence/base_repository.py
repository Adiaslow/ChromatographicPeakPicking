# src/chromatographicpeakpicking/infrastructure/persistence/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from ...core.protocols.serializable import Serializable

T = TypeVar('T', bound=Serializable)

class BaseRepository(ABC, Generic[T]):
    """Base class for all repositories."""

    @abstractmethod
    def save(self, entity: T) -> None:
        """Save an entity."""
        pass

    @abstractmethod
    def get(self, id: Any) -> Optional[T]:
        """Get an entity by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass

    @abstractmethod
    def delete(self, id: Any) -> None:
        """Delete an entity."""
        pass
