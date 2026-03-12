"""Cast file upload endpoint tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cli2ansible.adapters.outbound.capture.asciinema_parser import AsciinemaParser
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.api import create_app
from cli2ansible.application import CompilePlaybookService, IngestSessionService
from cli2ansible.domain.ports import ObjectStorePort


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

    def bucket_exists(self) -> bool:
        return True


@pytest.fixture
def cast_client() -> TestClient:
    """Create test client with parser and store configured for cast uploads."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    store = MockObjectStore()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()
    parser = AsciinemaParser()

    ingest = IngestSessionService(repo, parser, store)
    compile_svc = CompilePlaybookService(repo, translator, generator, store)

    app = create_app(ingest, compile_svc)
    return TestClient(app)


def test_upload_cast_file_success(cast_client: TestClient) -> None:
    """Test successful .cast file upload."""
    # Create session first
    create_resp = cast_client.post(
        "/api/v1/sessions", json={"name": "test-session", "metadata": {}}
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    # Load the demo.cast fixture
    fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"
    assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

    # Upload the cast file
    with open(fixture_path, "rb") as f:
        response = cast_client.post(
            f"/api/v1/sessions/{session_id}/cast",
            files={"file": ("demo.cast", f, "application/octet-stream")},
        )

    # Assert response
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()

    # Verify expected response fields (without user_name)
    assert data["status"] == "parsed"
    assert data["cast_file_key"] == f"sessions/{session_id}/recording.cast"
    assert data["event_count"] > 0
    assert "events" in data
    assert len(data["events"]) == data["event_count"]

    # Verify response only contains expected keys
    expected_keys = {"status", "cast_file_key", "event_count", "events"}
    assert (
        set(data.keys()) == expected_keys
    ), f"Unexpected keys in response: {set(data.keys()) - expected_keys}"


def test_upload_cast_file_invalid_extension(cast_client: TestClient) -> None:
    """Test that non-.cast files are rejected."""
    # Create session first
    create_resp = cast_client.post(
        "/api/v1/sessions", json={"name": "test-session", "metadata": {}}
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    # Try to upload a file with wrong extension
    response = cast_client.post(
        f"/api/v1/sessions/{session_id}/cast",
        files={"file": ("test.txt", b"some content", "text/plain")},
    )

    # Should be rejected with 400
    assert response.status_code == 400
    assert "cast" in response.json()["detail"].lower()


def test_upload_cast_file_no_filename(cast_client: TestClient) -> None:
    """Test that files without filename are rejected."""
    # Create session first
    create_resp = cast_client.post(
        "/api/v1/sessions", json={"name": "test-session", "metadata": {}}
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    # Try to upload a file with empty filename
    response = cast_client.post(
        f"/api/v1/sessions/{session_id}/cast",
        files={"file": ("", b"some content", "application/octet-stream")},
    )

    # FastAPI returns 422 for validation errors, or 400 if our handler catches it
    assert response.status_code in (400, 422)


def test_upload_cast_file_session_not_found(cast_client: TestClient) -> None:
    """Test that uploading to non-existent session returns 404."""
    # Use a random UUID that doesn't exist
    fake_session_id = "00000000-0000-0000-0000-000000000000"

    fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"
    with open(fixture_path, "rb") as f:
        response = cast_client.post(
            f"/api/v1/sessions/{fake_session_id}/cast",
            files={"file": ("demo.cast", f, "application/octet-stream")},
        )

    # Should return 404
    assert response.status_code == 404
