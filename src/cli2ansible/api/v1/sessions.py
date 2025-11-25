"""Session management and operations router.

Consolidates all /sessions endpoints including:
- Session CRUD operations
- Playbook compilation
- Session cleaning
- Translation reports
"""
# noqa: F841

from typing import Any
from uuid import UUID

from cli2ansible.api.schemas import (
    ArtifactResponse,
    CleanSessionResponse,
    CompileRequest,
    MostCommonCommand,
    ReportResponse,
    SessionCreate,
    SessionResponse,
)
from cli2ansible.application.dtos import SessionResponseDTO
from cli2ansible.application.errors import ServiceUnavailableError
from cli2ansible.application.ports import (
    CleanSessionUseCase,
    CompilePlaybookUseCase,
    IngestSessionUseCase,
)
from fastapi import APIRouter


def create_router(
    ingest_service: IngestSessionUseCase,
    compile_service: CompilePlaybookUseCase,
    clean_service: CleanSessionUseCase | None = None,
) -> APIRouter:
    """Create and return the consolidated sessions router.

    Args:
        ingest_service: Service for ingesting session data
        compile_service: Service for compiling playbooks
        clean_service: Service for cleaning sessions (optional)

    Returns:
        Configured APIRouter instance
    """
    router = APIRouter(prefix="/sessions", tags=["sessions"])

    # ============ Session CRUD Operations ============

    @router.post("", response_model=SessionResponse)
    async def create_session(req: SessionCreate) -> SessionResponseDTO:
        """Create a new session.

        Args:
            req: Session creation request with name and optional metadata

        Returns:
            SessionResponse with created session details

        Raises:
            ApplicationError: If validation fails
        """
        from cli2ansible.application.dtos import SessionCreateRequestDTO

        request_dto = SessionCreateRequestDTO(
            name=req.name,
            metadata=req.metadata or {},
            tags=req.tags or []
        )
        return ingest_service.create_session(request_dto)

    @router.get("", tags=["sessions"])
    async def list_sessions(tags: str | None = None) -> dict[str, list[SessionResponseDTO]]:
        """List all sessions, optionally filtered by tags.

        Args:
            tags: Comma-separated list of tags to filter by (e.g., "production,database")

        Returns:
            Dictionary with sessions list
        """
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        sessions = ingest_service.list_sessions(tags=tag_list)
        return {"sessions": sessions}

    @router.get("/{session_id}", response_model=SessionResponse)
    async def get_session(session_id: UUID) -> SessionResponseDTO:
        """Get session by ID.

        Args:
            session_id: UUID of session to retrieve

        Returns:
            SessionResponse with session details

        Raises:
            ApplicationError: 404 if session not found
        """
        return ingest_service.get_session(session_id)

    @router.delete("/{session_id}")
    async def delete_session(session_id: UUID) -> dict[str, str]:
        """Delete a session and all related data.

        Args:
            session_id: UUID of session to delete

        Returns:
            Success message

        Raises:
            ApplicationError: 404 if session not found
        """
        ingest_service.delete_session(session_id)
        return {"message": "Session deleted successfully"}

    # ============ Compilation Endpoint ============

    @router.post("/{session_id}/compile", response_model=ArtifactResponse)
    async def compile_session(
        session_id: UUID,
        request: CompileRequest | None = None,  # kept for API consistency
    ) -> Any:
        """Compile session to Ansible playbook.

        Orchestrates the full compilation flow:
        - Extracts commands from events
        - Compiles to Ansible role
        - Exports artifact to storage
        - Returns download URLs
        """
        _ = request  # Mark as used for API consistency
        return compile_service.compile(session_id)

    # ============ Report Endpoint ============

    @router.get("/{session_id}/report", response_model=ReportResponse)
    async def get_report(session_id: UUID) -> ReportResponse:
        """Get translation report for a session.

        Generates comprehensive translation report showing:
        - Command counts and confidence levels
        - Module usage breakdown
        - Most common commands
        - Warnings and skipped commands
        - Session statistics
        """
        # Get or generate report
        report = compile_service.get_report(session_id)

        return ReportResponse(
            session_id=report.session_id,
            total_commands=report.total_commands,
            high_confidence=report.high_confidence,
            medium_confidence=report.medium_confidence,
            low_confidence=report.low_confidence,
            warnings=report.warnings,
            skipped_commands=report.skipped_commands,
            generated_at=report.generated_at,
            module_breakdown=report.module_breakdown,
            high_confidence_percentage=report.high_confidence_percentage,
            medium_confidence_percentage=report.medium_confidence_percentage,
            low_confidence_percentage=report.low_confidence_percentage,
            session_duration_seconds=report.session_duration_seconds,
            most_common_commands=[
                MostCommonCommand(command=cmd, count=count)
                for cmd, count in report.most_common_commands
            ],
            sudo_command_count=report.sudo_command_count,
        )

    # ============ Cleaning Endpoint ============

    @router.post("/{session_id}/clean", response_model=CleanSessionResponse)
    async def clean_session(session_id: UUID) -> Any:
        """Clean terminal session by removing duplicates and error corrections.

        Uses LLM-based analysis to intelligently clean commands:
        - Identify and remove duplicate commands
        - Detect and remove error corrections (typo fixes, etc.)
        - Keep only meaningful, unique commands
        """
        if clean_service is None:
            raise ServiceUnavailableError(
                "Clean service not available. Configure ANTHROPIC_API_KEY."
            )

        result: Any = clean_service.clean(session_id)
        return result

    return router
