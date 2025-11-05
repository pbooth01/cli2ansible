"""API tests for the /clean endpoint."""

from uuid import uuid4

import pytest
from cli2ansible.adapters.inbound.http.api import create_app
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.models import CleanedCommand, CleaningReport, Command
from cli2ansible.domain.ports import LLMPort, ObjectStorePort
from cli2ansible.domain.services import CleanSession, CompilePlaybook, IngestSession
from fastapi.testclient import TestClient


class MockObjectStore(ObjectStorePort):
    """Mock object store for testing."""

    def __init__(self) -> None:
        self.storage: dict[str, bytes] = {}

    def upload(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        self.storage[key] = data
        return key

    def download(self, key: str) -> bytes:
        return self.storage.get(key, b"")

    def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]

    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        return f"http://mock/{key}"


class MockLLMPort(LLMPort):
    """Mock LLM port for testing."""

    def clean_commands(
        self, commands: list[Command], session_id: object
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """Mock implementation of clean_commands."""
        if not commands:
            return [], CleaningReport(
                session_id=session_id,
                original_command_count=0,
                cleaned_command_count=0,
                duplicates_removed=0,
                error_corrections_removed=0,
                cleaning_rationale="No commands",
            )

        # Return a simplified version (remove duplicates)
        seen = set()
        cleaned = []
        duplicates = 0

        for cmd in commands:
            if cmd.normalized not in seen:
                seen.add(cmd.normalized)
                cleaned.append(
                    CleanedCommand(
                        session_id=session_id,
                        command=cmd.normalized,
                        reason="Essential command",
                        first_occurrence=cmd.timestamp,
                        occurrence_count=1,
                        is_duplicate=False,
                        is_error_correction=False,
                    )
                )
            else:
                duplicates += 1

        report = CleaningReport(
            session_id=session_id,
            original_command_count=len(commands),
            cleaned_command_count=len(cleaned),
            duplicates_removed=duplicates,
            error_corrections_removed=0,
            cleaning_rationale=f"Removed {duplicates} duplicate commands",
        )

        return cleaned, report


@pytest.fixture()
def client_with_clean_service() -> TestClient:
    """Create test client with clean service enabled."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    store = MockObjectStore()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()
    mock_llm = MockLLMPort()

    ingest = IngestSession(repo)
    compile_svc = CompilePlaybook(repo, translator, generator, store)
    clean_svc = CleanSession(repo, mock_llm)

    app = create_app(ingest, compile_svc, clean_svc)
    return TestClient(app)


@pytest.fixture()
def client_without_clean_service() -> TestClient:
    """Create test client without clean service (simulating missing API key)."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    store = MockObjectStore()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()

    ingest = IngestSession(repo)
    compile_svc = CompilePlaybook(repo, translator, generator, store)

    app = create_app(ingest, compile_svc, clean_service=None)
    return TestClient(app)


def test_clean_session_endpoint_success(client_with_clean_service: TestClient) -> None:
    """Test POST /sessions/{session_id}/clean with valid session."""
    # Arrange: Create session with commands
    create_resp = client_with_clean_service.post(
        "/sessions", json={"name": "test-session", "metadata": {}}
    )
    session_id = create_resp.json()["id"]

    # Upload events
    events = [
        {
            "timestamp": 1.0,
            "event_type": "o",
            "data": "apt-get install nginx\n",
            "sequence": 0,
        },
        {
            "timestamp": 2.0,
            "event_type": "o",
            "data": "apt-get install nginx\n",
            "sequence": 1,
        },
        {
            "timestamp": 3.0,
            "event_type": "o",
            "data": "systemctl start nginx\n",
            "sequence": 2,
        },
    ]
    client_with_clean_service.post(f"/sessions/{session_id}/events", json=events)

    # Act: Clean session
    response = client_with_clean_service.post(f"/sessions/{session_id}/clean")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert "cleaned_commands" in data
    assert "report" in data

    # Verify report structure
    report = data["report"]
    assert report["session_id"] == session_id
    assert "original_command_count" in report
    assert "cleaned_command_count" in report
    assert "duplicates_removed" in report
    assert "error_corrections_removed" in report
    assert "cleaning_rationale" in report
    assert "generated_at" in report


def test_clean_session_with_duplicate_removal(
    client_with_clean_service: TestClient,
) -> None:
    """Test that duplicates are properly detected and reported."""
    # Arrange: Create session with duplicate commands
    create_resp = client_with_clean_service.post(
        "/sessions", json={"name": "test-session", "metadata": {}}
    )
    session_id = create_resp.json()["id"]

    # Upload duplicate events
    events = [
        {"timestamp": 1.0, "event_type": "o", "data": "echo hello\n", "sequence": 0},
        {"timestamp": 2.0, "event_type": "o", "data": "echo hello\n", "sequence": 1},
        {"timestamp": 3.0, "event_type": "o", "data": "echo hello\n", "sequence": 2},
    ]
    client_with_clean_service.post(f"/sessions/{session_id}/events", json=events)

    # Act
    response = client_with_clean_service.post(f"/sessions/{session_id}/clean")

    # Assert
    assert response.status_code == 200
    data = response.json()
    report = data["report"]

    # Should have fewer cleaned commands than original
    assert report["cleaned_command_count"] < report["original_command_count"]
    assert report["duplicates_removed"] > 0


def test_clean_session_not_found(client_with_clean_service: TestClient) -> None:
    """Test POST /clean with non-existent session returns 404."""
    # Act
    fake_session_id = uuid4()
    response = client_with_clean_service.post(f"/sessions/{fake_session_id}/clean")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_clean_session_without_service_configured(
    client_without_clean_service: TestClient,
) -> None:
    """Test POST /clean when clean service is not configured returns 503."""
    # Arrange: Create session (service exists but clean_service is None)
    create_resp = client_without_clean_service.post(
        "/sessions", json={"name": "test-session", "metadata": {}}
    )
    session_id = create_resp.json()["id"]

    # Act
    response = client_without_clean_service.post(f"/sessions/{session_id}/clean")

    # Assert
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "not available" in detail.lower()
    assert "ANTHROPIC_API_KEY" in detail or "configure" in detail.lower()


def test_clean_empty_session(client_with_clean_service: TestClient) -> None:
    """Test cleaning a session with no commands."""
    # Arrange: Create empty session
    create_resp = client_with_clean_service.post(
        "/sessions", json={"name": "empty-session", "metadata": {}}
    )
    session_id = create_resp.json()["id"]

    # Act: Clean without uploading any events
    response = client_with_clean_service.post(f"/sessions/{session_id}/clean")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data["cleaned_commands"]) == 0
    assert data["report"]["original_command_count"] == 0
    assert data["report"]["cleaned_command_count"] == 0
    assert data["report"]["duplicates_removed"] == 0
    assert data["report"]["error_corrections_removed"] == 0
