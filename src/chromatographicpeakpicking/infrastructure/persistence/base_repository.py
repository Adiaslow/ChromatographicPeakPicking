# src/chromatographicpeakpicking/infrastructure/persistence/base_repository.py

"""
Base repository for persistence layer.
"""

class BaseRepository:
    def save(self, entity):
        """
        Save an entity to the repository.

        Args:
            entity: The entity to save.
        """
        raise NotImplementedError("Save method not implemented.")

    def get(self, entity_id):
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: The ID of the entity to retrieve.
        """
        raise NotImplementedError("Get method not implemented.")

    def get_all(self):
        """
        Retrieve all entities from the repository.
        """
        raise NotImplementedError("Get all method not implemented.")

    def delete(self, entity_id):
        """
        Delete an entity by its ID.

        Args:
            entity_id: The ID of the entity to delete.
        """
        raise NotImplementedError("Delete method not implemented.")
