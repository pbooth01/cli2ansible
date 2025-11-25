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


def test_session_with_tags(repository: SQLAlchemyRepository) -> None:
    """Test session creation with tags and tag filtering."""
    ingest = IngestSessionService(repository)

    # Create sessions with different tags
    req1 = SessionCreateRequestDTO(
        name="prod-session",
        metadata={},
        tags=["production", "database"]
    )
    session1 = ingest.create_session(req1)
    assert session1.tags == ["production", "database"]

    req2 = SessionCreateRequestDTO(
        name="dev-session",
        metadata={},
        tags=["development", "database"]
    )
    session2 = ingest.create_session(req2)
    assert session2.tags == ["development", "database"]

    req3 = SessionCreateRequestDTO(
        name="test-session",
        metadata={},
        tags=["production", "web"]
    )
    session3 = ingest.create_session(req3)
    assert session3.tags == ["production", "web"]

    # List all sessions
    all_sessions = ingest.list_sessions()
    assert len(all_sessions) == 3

    # Filter by single tag
    prod_sessions = ingest.list_sessions(tags=["production"])
    assert len(prod_sessions) == 2
    assert all("production" in s.tags for s in prod_sessions)

    # Filter by multiple tags (AND logic)
    prod_db_sessions = ingest.list_sessions(tags=["production", "database"])
    assert len(prod_db_sessions) == 1
    assert prod_db_sessions[0].name == "prod-session"


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
