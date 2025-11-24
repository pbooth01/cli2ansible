"""Port for cast file persistence."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.domain.entities import CastFile


class CastFileRepositoryPort(ABC):
    """Port for cast file persistence."""

    @abstractmethod
    def save_cast_file(self, cast_file: CastFile) -> CastFile:
        """Save a cast file record for a session."""
        ...

    @abstractmethod
    def get_cast_file(self, session_id: UUID) -> CastFile | None:
        """Get the most recent cast file for a session."""
        ...
