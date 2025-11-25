"""Input port for session ingestion use case."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.application.dtos import (
    EventCreateRequestDTO,
    EventResponseDTO,
    EventUpdateRequestDTO,
    SessionCreateRequestDTO,
    SessionResponseDTO,
)


class IngestSessionUseCase(ABC):
    """Use case for ingesting terminal sessions."""

    @abstractmethod
    def create_session(self, req: SessionCreateRequestDTO) -> SessionResponseDTO:
        """Create a new session."""
        ...

    @abstractmethod
    def get_session(self, session_id: UUID) -> SessionResponseDTO:
        """Get session by ID."""
        ...

    @abstractmethod
    def list_sessions(self) -> list[SessionResponseDTO]:
        """List all sessions."""
        ...

    @abstractmethod
    def delete_session(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        ...

    @abstractmethod
    def upload_cast_file(
        self, session_id: UUID, filename: str, file_data: bytes
    ) -> list[EventResponseDTO]:
        """Upload a .cast file to a session."""
        ...

    @abstractmethod
    def save_events(
        self, session_id: UUID, events: list[EventCreateRequestDTO]
    ) -> None:
        """Save events for a session."""
        ...

    @abstractmethod
    def get_events(self, session_id: UUID) -> list[EventResponseDTO]:
        """Get all events for a session."""
        ...

    @abstractmethod
    def update_event(
        self, session_id: UUID, event_id: UUID, req: EventUpdateRequestDTO
    ) -> EventResponseDTO:
        """Update a single event."""
        ...
