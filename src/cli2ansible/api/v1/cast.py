"""Cast file upload router."""
# noqa: F841

from typing import Any
from uuid import UUID

from cli2ansible.api.schemas import CastUploadResponse
from cli2ansible.api.v1.utils import event_dto_to_response
from cli2ansible.application.errors import BadRequestError
from fastapi import APIRouter, UploadFile


def create_router(ingest_service: Any, compile_service: Any) -> APIRouter:
    """Create and return the cast file router.

    Args:
        ingest_service: Service for ingesting session data
        compile_service: Service for compiling playbooks

    Returns:
        Configured APIRouter instance
    """
    router = APIRouter(prefix="/sessions", tags=["cast"])

    @router.post("/{session_id}/cast", response_model=CastUploadResponse)
    async def upload_cast_file(session_id: UUID, file: UploadFile) -> Any:
        """Upload a .cast file to a session and auto-compile.

        This endpoint:
        1. Validates the uploaded file has .cast extension and size limits
        2. Uses service to parse and store the .cast file into events
        3. Automatically extracts commands and compiles the playbook
        4. Returns parsed events

        Args:
            session_id: UUID of the target session
            file: Uploaded .cast file

        Returns:
            CastUploadResponse with parsed events and status

        Raises:
            ApplicationError: 400 if file validation fails, 404 if session not found, 413 if file too large
        """
        # Validate file extension (HTTP concern, not service logic)
        if not file.filename or not file.filename.endswith(".cast"):
            raise BadRequestError("File must have .cast extension")

        # Read file data
        file_data = await file.read()

        # Use service to upload cast file and auto-compile
        # Service handles: upload → parse → store → auto-compile (with graceful failure)
        # The service will validate file size and raise TooLarge if needed
        event_dtos = ingest_service.upload_cast_file_and_auto_compile(
            session_id, file.filename, file_data, compile_service
        )

        # Convert DTOs to Pydantic models at the API layer boundary
        events = [event_dto_to_response(dto) for dto in event_dtos]

        return CastUploadResponse(
            status="parsed",
            cast_file_key=f"sessions/{session_id}/recording.cast",
            event_count=len(events),
            events=events,
        )

    return router
