"""API endpoint tests."""

import pytest
from cli2ansible.adapters.inbound.http.api import create_app
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.ports import ObjectStorePort
from cli2ansible.domain.services import CompilePlaybook, IngestSession
from fastapi.testclient import TestClient


class MockObjectStore(ObjectStorePort):
    """Mock object store for testing."""

    def __init__(self) -> None:
        self.storage: dict[str, bytes] = {}

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self.storage[key] = data

        return key

    def download(self, key: str) -> bytes:
        return self.storage.get(key, b"")

    def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]

    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        return f"http://mock/{key}"


@pytest.fixture()
def client() -> TestClient:
    """Create test client."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    store = MockObjectStore()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()

    ingest = IngestSession(repo)
    compile_svc = CompilePlaybook(repo, translator, generator, store)

    app = create_app(ingest, compile_svc)
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_session(client: TestClient) -> None:
    """Test session creation."""
    response = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert "id" in data


def test_get_session(client: TestClient) -> None:
    """Test getting a session."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Get session
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_upload_events(client: TestClient) -> None:
    """Test uploading events."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Upload events
    events = [
        {"timestamp": 1.0, "event_type": "o", "data": "echo hello\n", "sequence": 0}
    ]
    response = client.post(f"/sessions/{session_id}/events", json=events)
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
