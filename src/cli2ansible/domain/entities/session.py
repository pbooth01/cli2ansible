"""Session domain entities."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from cli2ansible.domain.entities.enums import SessionStatus


@dataclass
class Session:
    """Terminal session recording."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    status: SessionStatus = SessionStatus.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CastFile:
    """Uploaded cast file for a session."""

    session_id: UUID
    file_name: str
    file_size: int  # Size in bytes
    id: UUID = field(default_factory=uuid4)
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Event:
    """Terminal event from recording."""

    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int = 0
    id: UUID = field(default_factory=uuid4)
    version: int = 1
