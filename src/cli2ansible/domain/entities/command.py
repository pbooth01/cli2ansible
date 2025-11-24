"""Command domain entity."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Command:
    """Parsed command from terminal session."""

    session_id: UUID
    raw: str
    normalized: str
    cwd: str = "/"
    user: str = "root"
    sudo: bool = False
    timestamp: float = 0.0
    exit_code: int | None = None
    output: str = ""
    event_sequence: int = 0  # Track which event this command came from
