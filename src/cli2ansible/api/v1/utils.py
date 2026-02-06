"""Utility functions for API routers."""

from typing import Any

from cli2ansible.api.schemas import (
    CastFileResponse,
    SessionResponse,
)
from cli2ansible.domain.entities import CastFile


def session_to_response(
    session: Any, cast_file: CastFile | None = None
) -> SessionResponse:
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
