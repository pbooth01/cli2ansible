"""Session-related DTOs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class SessionCreateRequestDTO:
    """Request to create a new session."""

    name: str
    metadata: dict[str, Any] | None = None


@dataclass
class SessionResponseDTO:
    """Response containing session information."""

    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
