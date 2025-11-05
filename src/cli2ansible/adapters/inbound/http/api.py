"""FastAPI HTTP adapter."""
from typing import Any
from uuid import UUID

from cli2ansible.domain.services import CompilePlaybook, IngestSession
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .schemas import (
    ArtifactResponse,
    CompileRequest,
    EventCreate,
    ReportResponse,
    SessionCreate,
    SessionResponse,
)


def create_app(
    ingest_service: IngestSession,
    compile_service: CompilePlaybook,
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
        from cli2ansible.app import get_repository

        repo = get_repository()
        session = repo.get(session_id)
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
    async def upload_events(session_id: UUID, events: list[EventCreate]) -> dict[str, str]:
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
        return {"status": "uploaded", "count": len(events)}

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
        from cli2ansible.app import get_object_store

        store = get_object_store()
        download_url = store.generate_url(artifact_key)

        return ArtifactResponse(
            artifact_url=artifact_key,
            download_url=download_url,
        )

    @app.get("/sessions/{session_id}/report", response_model=ReportResponse)
    async def get_report(session_id: UUID) -> Any:
        """Get translation report for a session."""
        from cli2ansible.app import get_repository

        repo = get_repository()
        session = repo.get(session_id)
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
        from cli2ansible.app import get_object_store

        store = get_object_store()
        artifact_key = f"sessions/{session_id}/role.zip"
        try:
            data = store.download(artifact_key)
            return StreamingResponse(
                iter([data]),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=role_{session_id}.zip"},
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Artifact not found: {str(e)}") from e

    return app
