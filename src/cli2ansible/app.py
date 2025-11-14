"""Application composition root."""

from cli2ansible.adapters.inbound.http.api import create_app
from cli2ansible.adapters.outbound.capture.asciinema_parser import AsciinemaParser
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.llm.anthropic_cleaner import AnthropicCleaner
from cli2ansible.adapters.outbound.llm.openai_cleaner import OpenAICleaner
from cli2ansible.adapters.outbound.object_store.s3_store import S3ObjectStore
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.ports import LLMPort
from cli2ansible.domain.services import CleanSession, CompilePlaybook, IngestSession
from cli2ansible.settings import settings

# Global instances (for dependency injection)
_repository: SQLAlchemyRepository | None = None
_object_store: S3ObjectStore | None = None
_llm_cleaner: LLMPort | None = None


def get_repository() -> SQLAlchemyRepository:
    """Get or create repository instance."""
    a = 1 / 0
    print(a)
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


def get_llm_cleaner() -> LLMPort:
    """Get or create LLM cleaner instance based on configured provider."""
    global _llm_cleaner
    if _llm_cleaner is None:
        provider = settings.llm_provider.lower()

        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            _llm_cleaner = OpenAICleaner(api_key=settings.openai_api_key)
        elif provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            _llm_cleaner = AnthropicCleaner(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Must be 'anthropic' or 'openai'")

    return _llm_cleaner


def create_services() -> tuple[IngestSession, CompilePlaybook, CleanSession | None]:
    """Create domain services with dependencies."""
    repo = get_repository()
    store = get_object_store()
    translator = RulesEngine()
    generator = AnsibleRoleGenerator()
    parser = AsciinemaParser()

    ingest_service = IngestSession(repo, parser, store)
    compile_service = CompilePlaybook(repo, translator, generator, store)

    # Only create clean service if LLM is configured
    clean_service: CleanSession | None = None
    provider = settings.llm_provider.lower()

    # Check if appropriate API key is configured
    if provider == "anthropic":
        has_api_key = bool(settings.anthropic_api_key)
    elif provider == "openai":
        has_api_key = bool(settings.openai_api_key)
    else:
        has_api_key = False

    if has_api_key:
        llm = get_llm_cleaner()
        clean_service = CleanSession(repo, llm)

    return ingest_service, compile_service, clean_service


# Create FastAPI app
ingest_service, compile_service, clean_service = create_services()
app = create_app(ingest_service, compile_service, clean_service)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
