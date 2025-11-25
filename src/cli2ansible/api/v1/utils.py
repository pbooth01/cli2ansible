"""Utility functions for API routers."""

from typing import Any

from cli2ansible.api.schemas import (
    CastFileResponse,
    EventResponse,
    SessionResponse,
)
from cli2ansible.application.dtos import EventResponseDTO
from cli2ansible.domain.entities import CastFile


def session_to_response(session: Any, cast_file: CastFile | None = None) -> SessionResponse:
    """Convert session domain model to API response with optional cast file."""
    cast_file_response = None
    if cast_file:
        cast_file_response = CastFileResponse(
            id=cast_file.id,
            session_id=cast_file.session_id,
            file_name=cast_file.file_name,
            file_size=cast_file.file_size,
            uploaded_at=cast_file.uploaded_at,
        )
    return SessionResponse(
        id=session.id,
        name=session.name,
        status=session.status.value,
        created_at=session.created_at,
        updated_at=session.updated_at,
        metadata=session.metadata,
        cast_file=cast_file_response,
    )


def event_dto_to_response(dto: EventResponseDTO) -> EventResponse:
    """Convert EventResponseDTO to EventResponse Pydantic model.

    This function handles the conversion from application layer DTOs (dataclasses)
    to API layer Pydantic schemas at the layer boundary, maintaining proper
    separation of concerns in the hexagonal architecture.

    Args:
        dto: EventResponseDTO dataclass from application layer

    Returns:
        EventResponse Pydantic model for API layer
    """
    return EventResponse(
        id=dto.id,
        session_id=dto.session_id,
        timestamp=dto.timestamp,
        event_type=dto.event_type,
        data=dto.data,
        sequence=dto.sequence,
        version=dto.version,
    )
