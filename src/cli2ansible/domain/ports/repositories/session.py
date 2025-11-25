"""Port for session persistence (CRUD operations)."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.domain.entities import Command, Event, Session


class SessionRepositoryPort(ABC):
    """Port for session persistence (CRUD operations).

    Note: This is a facade port that includes session, event, and command operations.
    The SQLAlchemyRepository implementation delegates to separate repositories.
    """

    @abstractmethod
    def create(self, session: Session) -> Session:
        """Create a new session."""
        ...

    @abstractmethod
    def get(self, session_id: UUID) -> Session | None:
        """Retrieve a session by ID."""
        ...

    @abstractmethod
    def list_all(self, tags: list[str] | None = None) -> list[Session]:
        """List all sessions, optionally filtered by tags."""
        ...

    @abstractmethod
    def update(self, session: Session) -> Session:
        """Update session."""
        ...

    @abstractmethod
    def delete(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        ...

    # Event operations (delegated to EventRepositoryPort in implementation)
    @abstractmethod
    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        ...

    @abstractmethod
    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        ...

    @abstractmethod
    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        ...

    @abstractmethod
    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        ...

    @abstractmethod
    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        ...

    # Command operations (delegated to CommandRepositoryPort in implementation)
    @abstractmethod
    def save_commands(self, commands: list[Command]) -> None:
        """Save parsed commands."""
        ...

    @abstractmethod
    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        ...

    @abstractmethod
    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        ...
