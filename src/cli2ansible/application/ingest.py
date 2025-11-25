"""Application service for ingesting terminal sessions."""

from typing import Any
from uuid import UUID, uuid4

from cli2ansible.application.dtos import (
    EventCreateRequestDTO,
    EventResponseDTO,
    EventUpdateRequestDTO,
    SessionCreateRequestDTO,
    SessionResponseDTO,
)
from cli2ansible.application.errors import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    TooLargeError,
)
from cli2ansible.application.extraction import CommandExtractionService
from cli2ansible.application.ports import IngestSessionUseCase
from cli2ansible.domain.entities import Command, Event, Session, SessionStatus
from cli2ansible.domain.ports import CapturePort, ObjectStorePort, SessionRepositoryPort


class IngestSessionService(IngestSessionUseCase):
    """Application service for ingesting terminal sessions."""

    def __init__(
        self,
        repo: SessionRepositoryPort,
        extractor: CommandExtractionService,
        parser: CapturePort | None = None,
        store: ObjectStorePort | None = None,
    ) -> None:
        """Initialize ingest service with ports."""
        self.repo = repo
        self.extractor = extractor
        self.parser = parser
        self.store = store

    def create_session(self, req: SessionCreateRequestDTO) -> SessionResponseDTO:
        """Create a new session."""
        print(f"[INGEST] Creating new session: {req.name}")
        session = Session(name=req.name, metadata=req.metadata or {})
        created = self.repo.create(session)
        print(f"[INGEST] Session created successfully: {created.id}")
        return self._session_to_response(created)

    def get_session(self, session_id: UUID) -> SessionResponseDTO:
        """Get session by ID."""
        print(f"[INGEST] Retrieving session: {session_id}")
        session = self.repo.get(session_id)
        if not session:
            print(f"[INGEST ERROR] Session not found: {session_id}")
            raise NotFoundError(f"Session {session_id} not found")
        print(f"[INGEST] Session retrieved: {session.name}")
        return self._session_to_response(session)

    def list_sessions(self) -> list[SessionResponseDTO]:
        """List all sessions."""
        print("[INGEST] Listing all sessions")
        sessions = self.repo.list_all()
        print(f"[INGEST] Found {len(sessions)} sessions")
        return [self._session_to_response(s) for s in sessions]

    def delete_session(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        print(f"[INGEST] Deleting session: {session_id}")
        session = self.repo.get(session_id)
        if not session:
            print(f"[INGEST ERROR] Session not found for deletion: {session_id}")
            raise NotFoundError(f"Session {session_id} not found")
        self.repo.delete(session_id)
        print(f"[INGEST] Session deleted successfully: {session_id}")

    def upload_cast_file(
        self, session_id: UUID, filename: str, file_data: bytes
    ) -> list[EventResponseDTO]:
        """Upload .cast file, store, parse, and save events.

        Args:
            session_id: UUID of session to upload to
            filename: Name of the uploaded file
            file_data: Raw file bytes

        Returns:
            List of EventResponse objects for the parsed events

        Raises:
            NotFoundError: If session not found
            TooLargeError: If file size exceeds maximum
            BadRequestError: If file is invalid or dependencies not configured
        """
        print(f"[INGEST] Starting cast file upload for session {session_id}: {filename}")

        if not self.parser:
            raise BadRequestError("Parser not configured")
        if not self.store:
            raise BadRequestError("Object store not configured")

        # 1. Validate session exists
        print(f"[INGEST] Validating session exists: {session_id}")
        session = self.repo.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        # 2. Validate file size
        file_size_mb = len(file_data) / (1024 * 1024)
        print(f"[INGEST] Validating file size: {file_size_mb:.2f}MB")
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            raise TooLargeError("File size exceeds maximum (10MB)")

        # 3. Parse file to validate format
        print(f"[INGEST] Parsing cast file: {filename}")
        try:
            events = self.parser.parse_events(file_data)
            print(f"[INGEST] Parsed {len(events)} events from cast file")
        except Exception as e:
            print(f"[INGEST ERROR] Failed to parse cast file: {str(e)}")
            raise BadRequestError(
                f"Invalid .cast file format: {str(e)}", {"parse_error": str(e)}
            ) from e

        # 4. Store file in MinIO
        key = f"sessions/{session_id}/recording.cast"
        print(f"[INGEST] Storing file in object store: {key}")
        self.store.upload(key, file_data, "application/json")

        # 5. Assign event IDs and versions
        print(f"[INGEST] Assigning IDs and versions to {len(events)} events")
        for event in events:
            event.id = uuid4()
            event.session_id = session_id
            event.version = 1

        # 6. Save events to database
        print(f"[INGEST] Saving {len(events)} events to database")
        self.repo.save_events(events)

        # 7. Update session metadata and status
        print(f"[INGEST] Updating session metadata and status")
        session.metadata["cast_file_key"] = key
        session.metadata["cast_filename"] = filename
        session.status = SessionStatus.UPLOADED
        self.repo.update(session)

        print(f"[INGEST] Cast file upload completed successfully for session {session_id}")
        return [self._event_to_response(e) for e in events]

    def upload_cast_file_and_auto_compile(
        self,
        session_id: UUID,
        filename: str,
        file_data: bytes,
        compile_service: Any,
    ) -> list[EventResponseDTO]:
        """Upload .cast file and automatically compile the session.

        This is a higher-level orchestration method that:
        1. Uploads and parses the cast file
        2. Automatically compiles the session to generate Ansible playbook
        3. Gracefully handles compilation failures (logs but doesn't fail upload)

        Args:
            session_id: UUID of session to upload to
            filename: Name of the uploaded file
            file_data: Raw file bytes
            compile_service: CompilePlaybookService instance for auto-compile

        Returns:
            List of EventResponse objects for the parsed events.
            Compilation failures are logged but don't affect the return value.

        Raises:
            ValueError: If file upload fails (compilation failures are logged but not raised)
        """
        import logging

        logger = logging.getLogger(__name__)

        # Upload the cast file (this may raise ValueError if validation fails)
        events = self.upload_cast_file(session_id, filename, file_data)

        # Attempt auto-compile (but don't fail the upload if it fails)
        try:
            compile_service.compile(session_id)
        except Exception as e:
            logger.warning(f"Auto-compile after cast upload for session {session_id} failed: {e}")

        return events

    def save_events(self, session_id: UUID, events: list[EventCreateRequestDTO]) -> None:
        """Save events for a session."""
        print(f"[INGEST] Saving {len(events)} events for session {session_id}")
        session = self.repo.get(session_id)
        if not session:
            print(f"[INGEST ERROR] Session not found: {session_id}")
            raise NotFoundError(f"Session {session_id} not found")

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

        print(f"[INGEST] Updating session status to UPLOADED")
        session.status = SessionStatus.UPLOADED
        self.repo.update(session)
        self.repo.save_events(domain_events)
        print(f"[INGEST] Events saved successfully")

    def get_events(self, session_id: UUID) -> list[EventResponseDTO]:
        """Get all events for a session."""
        print(f"[INGEST] Retrieving events for session {session_id}")
        session = self.repo.get(session_id)
        if not session:
            print(f"[INGEST ERROR] Session not found: {session_id}")
            raise NotFoundError(f"Session {session_id} not found")

        events = self.repo.get_events(session_id)
        print(f"[INGEST] Retrieved {len(events)} events")
        return [self._event_to_response(e) for e in events]

    def update_event(
        self, session_id: UUID, event_id: UUID, req: EventUpdateRequestDTO
    ) -> EventResponseDTO:
        """Update a single event with optimistic locking."""
        event = self.repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")

        if event.session_id != session_id:
            raise NotFoundError("Event does not belong to this session")

        if req.version is not None and event.version != req.version:
            raise ConflictError(
                f"Version conflict: expected {req.version}, current is {event.version}",
                {"expected_version": req.version, "current_version": event.version},
            )

        # Apply updates
        if req.timestamp is not None:
            event.timestamp = req.timestamp
        if req.data is not None:
            event.data = req.data
        if req.event_type is not None:
            event.event_type = req.event_type

        # Increment version
        event.version += 1

        # Save
        updated = self.repo.update_event(event)
        return self._event_to_response(updated)

    def extract_commands(self, session_id: UUID) -> list[Command]:
        """Extract commands from session events.

        Delegates to CommandExtractionService for the actual extraction logic.
        """
        return self.extractor.extract_commands(session_id)

    @staticmethod
    def _session_to_response(session: Session) -> SessionResponseDTO:
        """Convert session to response DTO."""
        return SessionResponseDTO(
            id=session.id,
            name=session.name,
            status=session.status.value,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata,
        )

    @staticmethod
    def _event_to_response(event: Event) -> EventResponseDTO:
        """Convert event to response DTO."""
        return EventResponseDTO(
            id=event.id,
            session_id=event.session_id,
            timestamp=event.timestamp,
            event_type=event.event_type,
            data=event.data,
            sequence=event.sequence,
            version=event.version,
        )
