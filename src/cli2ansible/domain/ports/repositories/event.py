"""Port for event persistence."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.domain.entities import Event


class EventRepositoryPort(ABC):
    """Port for event persistence."""

    @abstractmethod
    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        ...

    @abstractmethod
    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        ...

    @abstractmethod
    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        ...

    @abstractmethod
    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        ...

    @abstractmethod
    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        ...
