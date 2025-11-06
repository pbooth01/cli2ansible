"""Shared test fixtures for API tests."""

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
