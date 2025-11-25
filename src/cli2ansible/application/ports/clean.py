"""Input port for session cleaning use case."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.application.dtos import CleanSessionResponseDTO


class CleanSessionUseCase(ABC):
    """Use case for cleaning terminal sessions."""

    @abstractmethod
    def clean(self, session_id: UUID) -> CleanSessionResponseDTO:
        """Clean terminal session by removing duplicates and error corrections."""
        ...
