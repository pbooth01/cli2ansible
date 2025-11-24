"""Event-related DTOs."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class EventCreateRequestDTO:
    """Request to create an event."""

    timestamp: float
    event_type: str
    data: str
    sequence: int


@dataclass
class EventResponseDTO:
    """Response containing event information."""

    id: UUID
    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int
    version: int


@dataclass
class EventUpdateRequestDTO:
    """Request to update an event."""

    timestamp: float | None = None
    data: str | None = None
    event_type: str | None = None
    version: int | None = None
