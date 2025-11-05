"""Application composition root."""
from cli2ansible.adapters.inbound.http.api import create_app
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.object_store.s3_store import S3ObjectStore
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.services import CompilePlaybook, IngestSession
from cli2ansible.settings import settings

# Global instances (for dependency injection)
_repository: SQLAlchemyRepository | None = None
_object_store: S3ObjectStore | None = None


def get_repository() -> SQLAlchemyRepository:
    """Get or create repository instance."""
    global _repository
    if _repository is None:
        _repository = SQLAlchemyRepository(settings.database_url)
        _repository.create_tables()
    return _repository


def get_object_store() -> S3ObjectStore:
    """Get or create object store instance."""
    global _object_store
    if _object_store is None:
        _object_store = S3ObjectStore(
            endpoint=settings.s3_endpoint,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            bucket=settings.s3_bucket,
        )
    return _object_store


def create_services() -> tuple[IngestSession, CompilePlaybook]:
    """Create domain services with dependencies."""
    repo = get_repository()
    store = get_object_store()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()

    ingest_service = IngestSession(repo)
    compile_service = CompilePlaybook(repo, translator, generator, store)

    return ingest_service, compile_service


# Create FastAPI app
ingest_service, compile_service = create_services()
app = create_app(ingest_service, compile_service)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
