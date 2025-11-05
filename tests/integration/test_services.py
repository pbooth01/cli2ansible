"""Integration tests for domain services."""
from uuid import UUID

import pytest

from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.domain.models import Event
from cli2ansible.domain.services import IngestSession


def test_session_lifecycle(repository: SQLAlchemyRepository) -> None:
    """Test session creation and retrieval."""
    ingest = IngestSession(repository)

    # Create session
    session = ingest.create_session("test-session", {"key": "value"})
    assert session.id is not None
    assert session.name == "test-session"

    # Retrieve session
    retrieved = repository.get(session.id)
    assert retrieved is not None
    assert retrieved.id == session.id
    assert retrieved.name == "test-session"


def test_event_ingestion(ingest_service: IngestSession, repository: SQLAlchemyRepository) -> None:
    """Test event ingestion."""
    session = ingest_service.create_session("test-session")

    events = [
        Event(
            session_id=session.id,
            timestamp=1.0,
            event_type="o",
            data="sudo apt-get install nginx\n",
            sequence=0,
        ),
        Event(
            session_id=session.id,
            timestamp=2.0,
            event_type="o",
            data="systemctl start nginx\n",
            sequence=1,
        ),
    ]

    ingest_service.save_events(session.id, events)

    # Verify events saved
    saved_events = repository.get_events(session.id)
    assert len(saved_events) == 2


def test_command_extraction(ingest_service: IngestSession, repository: SQLAlchemyRepository) -> None:
    """Test command extraction from events."""
    session = ingest_service.create_session("test-session")

    events = [
        Event(
            session_id=session.id,
            timestamp=1.0,
            event_type="o",
            data="apt-get install nginx\n",
            sequence=0,
        ),
    ]

    ingest_service.save_events(session.id, events)
    commands = ingest_service.extract_commands(session.id)

    assert len(commands) > 0
