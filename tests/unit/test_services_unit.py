"""Unit tests for application services."""


import pytest
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.application import CommandExtractionService, IngestSessionService


@pytest.fixture()
def repo() -> SQLAlchemyRepository:
    """Create in-memory repository for testing."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    return repo


@pytest.fixture()
def extractor(repo: SQLAlchemyRepository) -> CommandExtractionService:
    """Create CommandExtractionService."""
    return CommandExtractionService(repo)


@pytest.fixture()
def ingest_service(
    repo: SQLAlchemyRepository, extractor: CommandExtractionService
) -> IngestSessionService:
    """Create IngestSessionService."""
    return IngestSessionService(repo, extractor)


def test_extract_commands_with_newlines(
    ingest_service: IngestSessionService, repo: SQLAlchemyRepository
) -> None:
    """Test extract_commands with events that contain newlines."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create events with newlines
    from cli2ansible.application.dtos import EventCreateRequestDTO

    events_dto = [
        EventCreateRequestDTO(
            timestamp=0.001,
            event_type="o",
            data="mkdir test_1\n",
            sequence=0,
        ),
        EventCreateRequestDTO(
            timestamp=0.002,
            event_type="o",
            data="cd test_1\n",
            sequence=1,
        ),
        EventCreateRequestDTO(
            timestamp=0.003,
            event_type="o",
            data='echo "Hello Phillip"\n',
            sequence=2,
        ),
        EventCreateRequestDTO(
            timestamp=0.004,
            event_type="o",
            data="exit\n",
            sequence=3,
        ),
    ]

    # Save events
    ingest_service.save_events(session_id, events_dto)

    # Extract commands
    commands = ingest_service.extract_commands(session_id)

    # Verify commands were extracted
    assert len(commands) > 0
    command_texts = [cmd.raw for cmd in commands]
    print(f"Extracted commands: {command_texts}")


def test_extract_commands_without_newlines(
    ingest_service: IngestSessionService, repo: SQLAlchemyRepository
) -> None:
    """Test extract_commands with events that DON'T contain newlines."""
    from cli2ansible.application.dtos import EventCreateRequestDTO, SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create events WITHOUT newlines (like the user's example)
    events_dto = [
        EventCreateRequestDTO(
            timestamp=0.001,
            event_type="o",
            data="mkdir test_1",
            sequence=0,
        ),
        EventCreateRequestDTO(
            timestamp=0.001,
            event_type="o",
            data="cd test_1",
            sequence=1,
        ),
        EventCreateRequestDTO(
            timestamp=0.0,
            event_type="o",
            data='echo "Hello Phillip"',
            sequence=2,
        ),
        EventCreateRequestDTO(
            timestamp=0.001,
            event_type="o",
            data="exit",
            sequence=3,
        ),
    ]

    # Save events
    ingest_service.save_events(session_id, events_dto)

    # Extract commands
    commands = ingest_service.extract_commands(session_id)

    # Verify commands were extracted correctly
    print(f"Commands extracted: {len(commands)}")
    print(f"Command texts: {[cmd.raw for cmd in commands]}")

    assert len(commands) == 4
    command_texts = [cmd.raw for cmd in commands]
    assert "mkdir test_1" in command_texts
    assert "cd test_1" in command_texts
    assert 'echo "Hello Phillip"' in command_texts
    assert "exit" in command_texts
