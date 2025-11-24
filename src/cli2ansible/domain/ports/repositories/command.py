"""Port for command persistence."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.domain.entities import Command


class CommandRepositoryPort(ABC):
    """Port for command persistence."""

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
