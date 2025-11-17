"""Unit tests for domain services."""

import pytest
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.domain.models import Event
from cli2ansible.domain.services import IngestSession


@pytest.fixture()
def repo():
    """Create in-memory repository for testing."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    return repo


@pytest.fixture()
def ingest_service(repo):
    """Create IngestSession service."""
    return IngestSession(repo)


def test_extract_commands_with_newlines(ingest_service, repo):
    """Test extract_commands with events that contain newlines."""
    # Create session
    session = ingest_service.create_session("test-session")

    # Create events with newlines
    events = [
        Event(
            session_id=session.id,
            timestamp=0.001,
            event_type="o",
            data="mkdir test_1\n",
            sequence=0,
        ),
        Event(
            session_id=session.id,
            timestamp=0.002,
            event_type="o",
            data="cd test_1\n",
            sequence=1,
        ),
        Event(
            session_id=session.id,
            timestamp=0.003,
            event_type="o",
            data='echo "Hello Phillip"\n',
            sequence=2,
        ),
        Event(
            session_id=session.id,
            timestamp=0.004,
            event_type="o",
            data="exit\n",
            sequence=3,
        ),
    ]

    # Save events
    ingest_service.save_events(session.id, events)

    # Extract commands
    commands = ingest_service.extract_commands(session.id)

    # Verify commands were extracted
    assert len(commands) > 0
    command_texts = [cmd.raw for cmd in commands]
    print(f"Extracted commands: {command_texts}")


def test_extract_commands_without_newlines(ingest_service, repo):
    """Test extract_commands with events that DON'T contain newlines."""
    # Create session
    session = ingest_service.create_session("test-session")

    # Create events WITHOUT newlines (like the user's example)
    events = [
        Event(
            session_id=session.id,
            timestamp=0.001,
            event_type="o",
            data="mkdir test_1",
            sequence=0,
        ),
        Event(
            session_id=session.id,
            timestamp=0.001,
            event_type="o",
            data="cd test_1",
            sequence=1,
        ),
        Event(
            session_id=session.id,
            timestamp=0.0,
            event_type="o",
            data='echo "Hello Phillip"',
            sequence=2,
        ),
        Event(
            session_id=session.id,
            timestamp=0.001,
            event_type="o",
            data="exit",
            sequence=3,
        ),
    ]

    # Save events
    ingest_service.save_events(session.id, events)

    # Extract commands
    commands = ingest_service.extract_commands(session.id)

    # Verify commands were extracted correctly
    print(f"Commands extracted: {len(commands)}")
    print(f"Command texts: {[cmd.raw for cmd in commands]}")

    assert len(commands) == 4
    command_texts = [cmd.raw for cmd in commands]
    assert "mkdir test_1" in command_texts
    assert "cd test_1" in command_texts
    assert 'echo "Hello Phillip"' in command_texts
    assert "exit" in command_texts
