"""FastAPI HTTP adapter."""

from typing import Any
from uuid import UUID

from cli2ansible.domain.services import (
    CleanSession,
    CompilePlaybook,
    IngestSession,
    VersionConflictError,
)
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from .schemas import (
    ArtifactResponse,
    BatchEventUpdateRequest,
    BatchEventUpdateResponse,
    CastUploadResponse,
    CleanedCommandResponse,
    CleaningReportResponse,
    CleanSessionResponse,
    CompileRequest,
    EventCreate,
    EventResponse,
    EventsListResponse,
    EventUpdateRequest,
    EventUpdateResult,
    ReportResponse,
    SessionCreate,
    SessionResponse,
)


def create_app(
    ingest_service: IngestSession,
    compile_service: CompilePlaybook,
    clean_service: CleanSession | None = None,
) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="cli2ansible", version="0.1.0")

    @app.get("/")
    async def root() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "service": "cli2ansible"}

    @app.post("/sessions", response_model=SessionResponse)
    async def create_session(session: SessionCreate) -> Any:
        """Create a new session."""
        domain_session = ingest_service.create_session(
            name=session.name, metadata=session.metadata
        )
        return SessionResponse(
            id=domain_session.id,
            name=domain_session.name,
            status=domain_session.status.value,
            created_at=domain_session.created_at,
            updated_at=domain_session.updated_at,
            metadata=domain_session.metadata,
        )

    @app.get("/sessions/{session_id}", response_model=SessionResponse)
    async def get_session(session_id: UUID) -> Any:
        """Get session by ID."""
        session = ingest_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return SessionResponse(
            id=session.id,
            name=session.name,
            status=session.status.value,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata,
        )

    @app.post("/sessions/{session_id}/events")
    async def upload_events(
        session_id: UUID, events: list[EventCreate]
    ) -> dict[str, str]:
        """Upload events for a session."""
        from cli2ansible.domain.models import Event

        domain_events = [
            Event(
                session_id=session_id,
                timestamp=e.timestamp,
                event_type=e.event_type,
                data=e.data,
                sequence=e.sequence,
            )
            for e in events
        ]
        ingest_service.save_events(session_id, domain_events)
        return {"status": "uploaded", "count": str(len(events))}

    @app.post("/sessions/{session_id}/cast", response_model=CastUploadResponse)
    async def upload_cast_file(session_id: UUID, file: UploadFile) -> Any:
        """Upload a .cast file to a session."""
        # Validate file
        if not file.filename or not file.filename.endswith(".cast"):
            raise HTTPException(
                status_code=400, detail="File must have .cast extension"
            )

        # Read file data
        file_data = await file.read()

        # Validate size
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=413,
                detail=f"File size ({len(file_data)} bytes) exceeds maximum (10485760 bytes)",
            )

        try:
            # Upload and parse
            events = ingest_service.upload_cast_file(
                session_id, file_data, file.filename
            )

            return CastUploadResponse(
                status="parsed",
                cast_file_key=f"sessions/{session_id}/recording.cast",
                event_count=len(events),
                events=[
                    EventResponse(
                        id=e.id,
                        session_id=e.session_id,
                        timestamp=e.timestamp,
                        event_type=e.event_type,
                        data=e.data,
                        sequence=e.sequence,
                        version=e.version,
                    )
                    for e in events
                ],
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @app.get("/sessions/{session_id}/events", response_model=EventsListResponse)
    async def get_events(session_id: UUID) -> Any:
        """Get all events for a session."""
        session = ingest_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        events = ingest_service.repo.get_events(session_id)

        return EventsListResponse(
            session_id=session_id,
            event_count=len(events),
            events=[
                EventResponse(
                    id=e.id,
                    session_id=e.session_id,
                    timestamp=e.timestamp,
                    event_type=e.event_type,
                    data=e.data,
                    sequence=e.sequence,
                    version=e.version,
                )
                for e in events
            ],
        )

    @app.patch("/sessions/{session_id}/events", response_model=BatchEventUpdateResponse)
    async def update_events_batch(
        session_id: UUID, request: BatchEventUpdateRequest
    ) -> Any:
        """Update multiple events in a batch."""
        session = ingest_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert Pydantic models to dicts
        updates = [update.dict() for update in request.updates]

        # Process batch update
        results = ingest_service.update_events_batch(session_id, updates)

        # Count successes and failures
        updated = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")

        # Convert results to response format
        formatted_results = []
        for result in results:
            if result["status"] == "success":
                event = result["event"]
                formatted_results.append(
                    EventUpdateResult(
                        id=result["id"],
                        status="success",
                        event=EventResponse(
                            id=event.id,
                            session_id=event.session_id,
                            timestamp=event.timestamp,
                            event_type=event.event_type,
                            data=event.data,
                            sequence=event.sequence,
                            version=event.version,
                        ),
                    )
                )
            else:
                formatted_results.append(
                    EventUpdateResult(
                        id=result["id"], status="error", error=result.get("error")
                    )
                )

        # Return 207 if partial success, 200 if all succeeded
        response = BatchEventUpdateResponse(
            updated=updated, failed=failed, results=formatted_results
        )

        return response

    @app.patch("/sessions/{session_id}/events/{event_id}", response_model=EventResponse)
    async def update_single_event(
        session_id: UUID, event_id: UUID, request: EventUpdateRequest
    ) -> Any:
        """Update a single event."""
        session = ingest_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        try:
            # Build updates dict
            updates: dict[str, Any] = {}
            if request.timestamp is not None:
                updates["timestamp"] = request.timestamp
            if request.data is not None:
                updates["data"] = request.data
            if request.event_type is not None:
                updates["event_type"] = request.event_type

            # Update event
            updated_event = ingest_service.update_event(
                session_id, event_id, updates, request.version
            )

            return EventResponse(
                id=updated_event.id,
                session_id=updated_event.session_id,
                timestamp=updated_event.timestamp,
                event_type=updated_event.event_type,
                data=updated_event.data,
                sequence=updated_event.sequence,
                version=updated_event.version,
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except VersionConflictError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e

    @app.post("/sessions/{session_id}/compile", response_model=ArtifactResponse)
    async def compile_session(session_id: UUID, request: CompileRequest) -> Any:
        """Compile session to Ansible playbook."""
        # Extract commands first
        ingest_service.extract_commands(session_id)

        # Compile to role
        role, report = compile_service.compile(session_id)

        # Export artifact
        artifact_key = compile_service.export_artifact(role, session_id)

        # Generate download URL
        download_url = compile_service.store.generate_url(artifact_key)

        return ArtifactResponse(
            artifact_url=artifact_key,
            download_url=download_url,
        )

    @app.get("/sessions/{session_id}/report", response_model=ReportResponse)
    async def get_report(session_id: UUID) -> Any:
        """Get translation report for a session."""
        session = compile_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Re-compile to get report (in production, cache this)
        role, report = compile_service.compile(session_id)

        return ReportResponse(
            session_id=report.session_id,
            total_commands=report.total_commands,
            high_confidence=report.high_confidence,
            medium_confidence=report.medium_confidence,
            low_confidence=report.low_confidence,
            warnings=report.warnings,
            skipped_commands=report.skipped_commands,
            generated_at=report.generated_at,
        )

    @app.get("/sessions/{session_id}/playbook")
    async def download_playbook(session_id: UUID) -> StreamingResponse:
        """Download generated playbook artifact."""
        artifact_key = f"sessions/{session_id}/role.zip"
        try:
            data = compile_service.store.download(artifact_key)
            return StreamingResponse(
                iter([data]),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=role_{session_id}.zip"
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Artifact not found: {str(e)}"
            ) from e

    @app.post("/sessions/{session_id}/clean", response_model=CleanSessionResponse)
    async def clean_session(session_id: UUID) -> Any:
        """Clean terminal session by removing duplicates and error corrections."""
        if clean_service is None:
            raise HTTPException(
                status_code=503,
                detail="Clean service not available. Configure ANTHROPIC_API_KEY.",
            )

        session = ingest_service.repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Extract commands from events first
        ingest_service.extract_commands(session_id)

        # Validate command count before processing
        from cli2ansible.settings import settings

        commands = ingest_service.repo.get_commands(session_id)
        if len(commands) > settings.max_commands_for_cleaning:
            raise HTTPException(
                status_code=400,
                detail=f"Session has {len(commands)} commands, maximum {settings.max_commands_for_cleaning} allowed for cleaning",
            )

        cleaned_commands, report = clean_service.clean_commands(session_id)

        return CleanSessionResponse(
            cleaned_commands=[
                CleanedCommandResponse(
                    command=cmd.command,
                    reason=cmd.reason,
                    first_occurrence=cmd.first_occurrence,
                    occurrence_count=cmd.occurrence_count,
                    is_duplicate=cmd.is_duplicate,
                    is_error_correction=cmd.is_error_correction,
                )
                for cmd in cleaned_commands
            ],
            report=CleaningReportResponse(
                session_id=report.session_id,
                original_command_count=report.original_command_count,
                cleaned_command_count=report.cleaned_command_count,
                duplicates_removed=report.duplicates_removed,
                error_corrections_removed=report.error_corrections_removed,
                cleaning_rationale=report.cleaning_rationale,
                generated_at=report.generated_at,
            ),
        )

    return app
