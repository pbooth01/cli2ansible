"""Port interfaces (hexagonal architecture)."""
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from cli2ansible.domain.models import Command, Event, Report, Role, Session, Task


class CapturePort(ABC):
    """Port for parsing terminal recordings."""

    @abstractmethod
    def parse_events(self, recording_data: bytes) -> list[Event]:
        """Parse recording into events."""
        ...


class TranslatorPort(ABC):
    """Port for translating commands to Ansible tasks."""

    @abstractmethod
    def translate(self, command: Command) -> Task | None:
        """Translate a command to an Ansible task."""
        ...


class RoleGeneratorPort(ABC):
    """Port for generating Ansible role artifacts."""

    @abstractmethod
    def generate(self, role: Role, output_path: str) -> None:
        """Generate role directory structure."""
        ...


class SessionRepositoryPort(ABC):
    """Port for session persistence."""

    @abstractmethod
    def create(self, session: Session) -> Session:
        """Create a new session."""
        ...

    @abstractmethod
    def get(self, session_id: UUID) -> Session | None:
        """Retrieve a session by ID."""
        ...

    @abstractmethod
    def update(self, session: Session) -> Session:
        """Update session."""
        ...

    @abstractmethod
    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        ...

    @abstractmethod
    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        ...

    @abstractmethod
    def save_commands(self, commands: list[Command]) -> None:
        """Save parsed commands."""
        ...

    @abstractmethod
    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        ...


class ObjectStorePort(ABC):
    """Port for artifact storage."""

    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload artifact and return URL."""
        ...

    @abstractmethod
    def download(self, key: str) -> bytes:
        """Download artifact."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete artifact."""
        ...

    @abstractmethod
    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL."""
        ...
