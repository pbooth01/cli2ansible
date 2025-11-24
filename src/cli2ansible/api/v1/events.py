"""Event management router."""
# noqa: F841

from typing import Any
from uuid import UUID

from cli2ansible.api.schemas import (
    BatchEventUpdateRequest,
    BatchEventUpdateResponse,
    EventCreate,
    EventResponse,
    EventsListResponse,
    EventUpdateRequest,
    EventUpdateResult,
)
from cli2ansible.application.errors import ApplicationError
from fastapi import APIRouter


def create_router(ingest_service: Any) -> APIRouter:
    """Create and return the events router.

    Args:
        ingest_service: Service for ingesting session data

    Returns:
        Configured APIRouter instance
    """
    router = APIRouter(prefix="/sessions", tags=["events"])

    @router.post("/{session_id}/events")
    async def upload_events(session_id: UUID, events: list[EventCreate]) -> dict[str, str]:
        """Upload events for a session.

        Args:
            session_id: UUID of the target session
            events: List of events to upload

        Returns:
            Status dict with upload status and count

        Raises:
            ApplicationError: 404 if session not found, 400 if validation fails
        """
        from cli2ansible.application.dtos import EventCreateRequestDTO

        # Convert Pydantic models to DTOs
        event_dtos = [
            EventCreateRequestDTO(
                timestamp=e.timestamp,
                event_type=e.event_type,
                data=e.data,
                sequence=e.sequence,
            )
            for e in events
        ]
        # Use service to save events
        ingest_service.save_events(session_id, event_dtos)
        return {"status": "uploaded", "count": str(len(events))}

    @router.get("/{session_id}/events", response_model=EventsListResponse)
    async def get_events(session_id: UUID) -> Any:
        """Get all events for a session.

        Args:
            session_id: UUID of the target session

        Returns:
            EventsListResponse with all events

        Raises:
            ApplicationError: 404 if session not found
        """
        # Service validates session exists and retrieves events
        events = ingest_service.get_events(session_id)

        return EventsListResponse(
            session_id=session_id,
            event_count=len(events),
            events=events,
        )

    @router.patch("/{session_id}/events", response_model=BatchEventUpdateResponse)
    async def update_events_batch(session_id: UUID, request: BatchEventUpdateRequest) -> Any:
        """Update multiple events in a batch.

        This endpoint processes multiple event updates with optimistic locking
        via version numbers. Each update is processed independently and failures
        in one update don't prevent others from being processed.

        Args:
            session_id: UUID of the target session
            request: Batch update request with list of updates

        Returns:
            BatchEventUpdateResponse with results for each update

        Raises:
            ApplicationError: 404 if session not found (only on first failure)
        """
        from cli2ansible.application.dtos import EventUpdateRequestDTO

        updated = 0
        failed = 0
        formatted_results = []

        for update in request.updates:
            try:
                # Convert Pydantic model to DTO
                update_dto = EventUpdateRequestDTO(
                    timestamp=update.timestamp,
                    data=update.data,
                    event_type=update.event_type,
                    version=update.version,
                )

                # Service validates and updates event with optimistic locking
                updated_event = ingest_service.update_event(session_id, update.id, update_dto)

                formatted_results.append(
                    EventUpdateResult(
                        id=update.id,
                        status="success",
                        event=updated_event,
                    )
                )
                updated += 1
            except ApplicationError as e:
                formatted_results.append(
                    EventUpdateResult(id=update.id, status="error", error=str(e))
                )
                failed += 1

        return BatchEventUpdateResponse(updated=updated, failed=failed, results=formatted_results)

    @router.patch("/{session_id}/events/{event_id}", response_model=EventResponse)
    async def update_single_event(
        session_id: UUID, event_id: UUID, request: EventUpdateRequest
    ) -> Any:
        """Update a single event.

        This endpoint updates a single event with optimistic locking.
        The version number must match the current event version.

        Args:
            session_id: UUID of the target session
            event_id: UUID of the event to update
            request: Update request with version and optional field updates

        Returns:
            Updated EventResponse

        Raises:
            ApplicationError: 404 if session or event not found, 409 if version conflict
        """
        from cli2ansible.application.dtos import EventUpdateRequestDTO

        # Convert Pydantic model to DTO
        update_dto = EventUpdateRequestDTO(
            timestamp=request.timestamp,
            data=request.data,
            event_type=request.event_type,
            version=request.version,
        )

        # Service validates session, event, and applies update with optimistic locking
        return ingest_service.update_event(session_id, event_id, update_dto)

    return router
