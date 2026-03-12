# AGENTS.md - Python Backend

This file provides guidance for AI agents working on the cli2ansible Python backend.

## What This Component Does

The Python backend is a FastAPI application that:

1. **Ingests** terminal session recordings (asciinema .cast files)
2. **Parses** recordings to extract shell commands
3. **Cleans** commands using LLM services (Anthropic/OpenAI) to remove noise
4. **Translates** shell commands to Ansible tasks using a rules engine
5. **Generates** complete Ansible roles with molecule test scaffolding
6. **Stores** artifacts in S3-compatible object storage (MinIO)

## Architecture (Hexagonal/Ports & Adapters)

```
src/cli2ansible/
├── domain/                 # CORE: Pure business logic
│   ├── entities/           # Session, Command, Event, Task, Role
│   ├── ports/              # Interface contracts
│   └── exceptions.py       # Domain-specific errors
├── application/            # USE CASES: Orchestration
│   ├── ingest.py           # IngestSessionService
│   ├── compile.py          # CompilePlaybookService
│   └── clean.py            # CleanSessionService
├── adapters/outbound/      # I/O IMPLEMENTATIONS
│   ├── db/                 # SQLAlchemy repositories
│   ├── capture/            # Asciinema parser
│   ├── translator/         # Rules engine
│   ├── generators/         # Ansible role generator
│   ├── object_store/       # S3/MinIO storage
│   └── llm/                # LLM cleaners
└── api/                    # INBOUND: FastAPI endpoints
    └── v1/                 # Versioned API routes
```

## Running Tests

```bash
# All tests with coverage
poetry run pytest --cov=src/cli2ansible --cov-report=term-missing

# Unit tests only (fast, no Docker)
poetry run pytest tests/unit -v

# Integration tests (requires Docker services running)
make docker-up
poetry run pytest tests/integration -v

# API tests
poetry run pytest tests/api -v

# Specific test file
poetry run pytest tests/unit/test_translator.py -v

# Tests matching pattern
poetry run pytest -k "test_compile" -v
```

## Test Structure

| Directory | Purpose | Docker Required |
|-----------|---------|-----------------|
| `tests/unit/` | Unit tests for individual components | No |
| `tests/integration/` | Integration tests with real services | Yes |
| `tests/api/` | HTTP endpoint tests with TestClient | No |
| `tests/fixtures/` | Test data (cast files, expected outputs) | N/A |

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Application entry point, dependency injection |
| `settings.py` | Environment configuration (pydantic-settings) |
| `cli.py` | Click CLI commands |
| `api/__init__.py` | FastAPI app factory |
| `domain/ports/__init__.py` | Port interfaces |
| `application/ingest.py` | Session ingestion use case |
| `application/compile.py` | Playbook compilation use case |

## Code Quality Commands

```bash
# Linting
poetry run ruff check src/cli2ansible

# Type checking
poetry run mypy src/cli2ansible

# Formatting
poetry run black src/cli2ansible
poetry run ruff check --fix src/cli2ansible
```

## Environment Variables

Key settings (see `settings.py`):
- `DATABASE_URL` - PostgreSQL connection string
- `S3_ENDPOINT_URL` - MinIO/S3 endpoint
- `S3_BUCKET_NAME` - Storage bucket
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` - LLM credentials
- `LLM_PROVIDER` - Which LLM to use ("anthropic" or "openai")

## Development Workflow

1. Start Docker services: `make docker-up`
2. Run migrations: `make migrate`
3. Run tests: `poetry run pytest`
4. Run the API: `poetry run uvicorn cli2ansible.app:app --reload`

