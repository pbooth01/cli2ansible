"""Pytest fixtures."""
import pytest
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.services import IngestSession


@pytest.fixture()
def in_memory_db() -> str:
    """In-memory SQLite database URL."""
    return "sqlite:///:memory:"


@pytest.fixture()
def repository(in_memory_db: str) -> SQLAlchemyRepository:
    """Create repository with in-memory database."""
    repo = SQLAlchemyRepository(in_memory_db)
    repo.create_tables()
    return repo


@pytest.fixture()
def translator() -> RulesEngine:
    """Create translator."""
    return RulesEngine()


@pytest.fixture()
def generator() -> AnsibleRoleGenerator:
    """Create role generator."""
    return AnsibleRoleGenerator()


@pytest.fixture()
def ingest_service(repository: SQLAlchemyRepository) -> IngestSession:
    """Create ingest service."""
    return IngestSession(repository)
