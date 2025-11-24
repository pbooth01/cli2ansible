"""Integration tests for application services."""

from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.application import IngestSessionService
from cli2ansible.application.dtos import EventCreateRequestDTO, SessionCreateRequestDTO


def test_session_lifecycle(repository: SQLAlchemyRepository) -> None:
    """Test session creation and retrieval."""
    ingest = IngestSessionService(repository)

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={"key": "value"})
    session_dto = ingest.create_session(req)
    assert session_dto.id is not None
    assert session_dto.name == "test-session"

    # Retrieve session
    retrieved = repository.get(session_dto.id)
    assert retrieved is not None
    assert retrieved.id == session_dto.id
    assert retrieved.name == "test-session"


def test_event_ingestion(
    ingest_service: IngestSessionService, repository: SQLAlchemyRepository
) -> None:
    """Test event ingestion."""
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    events_dto = [
        EventCreateRequestDTO(
            timestamp=1.0,
            event_type="o",
            data="sudo apt-get install nginx\n",
            sequence=0,
        ),
        EventCreateRequestDTO(
            timestamp=2.0,
            event_type="o",
            data="systemctl start nginx\n",
            sequence=1,
        ),
    ]

    ingest_service.save_events(session_id, events_dto)

    # Verify events saved
    saved_events = repository.get_events(session_id)
    assert len(saved_events) == 2


def test_command_extraction(
    ingest_service: IngestSessionService, repository: SQLAlchemyRepository
) -> None:
    """Test command extraction from events."""
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    events_dto = [
        EventCreateRequestDTO(
            timestamp=1.0,
            event_type="o",
            data="apt-get install nginx\n",
            sequence=0,
        ),
    ]

    ingest_service.save_events(session_id, events_dto)

    commands = ingest_service.extract_commands(session_id)

    assert len(commands) > 0
