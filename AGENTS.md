# AGENTS.md

This file provides guidance for AI agents working on the cli2ansible project.

## Project Overview

**cli2ansible** is a service that captures terminal session recordings (e.g., from asciinema) and translates them into idempotent Ansible playbooks and roles. It enables DevOps engineers to convert ad-hoc command-line workflows into Infrastructure-as-Code (IaC).

## Project Structure

```
cli2ansible/
├── src/cli2ansible/          # Python backend (FastAPI + Hexagonal Architecture)
│   ├── domain/               # Core business logic (pure, no I/O)
│   │   ├── entities/         # Domain entities (Session, Command, Event)
│   │   ├── ports/            # Port interfaces (contracts)
│   │   ├── artifacts.py      # Role artifact exporter
│   │   └── exceptions.py     # Domain exceptions
│   ├── application/          # Application layer (use cases)
│   │   ├── ingest.py         # Session ingestion service
│   │   ├── compile.py        # Playbook compilation service
│   │   ├── clean.py          # LLM-based command cleaning
│   │   └── dtos/             # Data transfer objects
│   ├── adapters/             # I/O implementations
│   │   └── outbound/         # External integrations
│   │       ├── db/           # PostgreSQL repositories (SQLAlchemy)
│   │       ├── capture/      # Asciinema parser
│   │       ├── translator/   # Command-to-Ansible rules engine
│   │       ├── generators/   # Ansible role generation
│   │       ├── object_store/ # S3/MinIO storage
│   │       └── llm/          # Anthropic/OpenAI cleaners
│   ├── api/                  # FastAPI HTTP endpoints (v1)
│   ├── app.py                # Application entry point
│   └── settings.py           # Configuration
├── frontend/                 # Next.js 14 web UI
├── tests/                    # Pytest test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── api/                  # API endpoint tests
├── alembic/                  # Database migrations
├── docker-compose.yml        # Docker services (Postgres, MinIO, app, frontend)
├── Makefile                  # Development commands
└── pyproject.toml            # Python dependencies (Poetry)
```

## Architecture

The project follows **Hexagonal Architecture** (Ports & Adapters):

```
API (Inbound) → Application → Domain ← Adapters (Outbound)
                                ↑
                              Ports (Interfaces)
```

- **Domain Layer**: Pure business logic, no external dependencies
- **Application Layer**: Use cases orchestrating domain logic
- **Adapters Layer**: I/O implementations (database, storage, LLM)
- **API Layer**: FastAPI HTTP endpoints

## Running Tests

### Prerequisites
- Python 3.11+
- Poetry installed
- Docker (for integration tests)

### Test Commands

```bash
# Install dependencies
make dev-install

# Run all tests with coverage
make test
# or: poetry run pytest --cov=src --cov-report=html --cov-report=term

# Run unit tests only (no Docker required)
make test-unit
# or: poetry run pytest -m "not integration" --cov=src

# Run integration tests only (requires Docker services)
make test-integration
# or: poetry run pytest -m integration

# Run specific test file
poetry run pytest tests/unit/test_translator.py

# Run tests with verbose output
poetry run pytest -v

# Run tests matching a pattern
poetry run pytest -k "test_session"
```

### Test Organization

- `tests/unit/` - Unit tests (fast, no external dependencies)
- `tests/integration/` - Integration tests (require Docker services)
- `tests/api/` - API endpoint tests (use FastAPI TestClient)
- `tests/fixtures/` - Test data (cast files, expected outputs)

## Code Quality

```bash
# Run linter
make lint
# or: poetry run ruff check .

# Run type checker
make type-check
# or: poetry run mypy src

# Format code
make format
# or: poetry run ruff check --fix . && poetry run black .
```

## Docker Services

```bash
# Start services (Postgres, MinIO)
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs

# Clean up (remove volumes)
make docker-clean
```

## Key Entry Points

- **API**: `src/cli2ansible/app.py` - FastAPI application
- **CLI**: `src/cli2ansible/cli.py` - Command-line interface
- **Settings**: `src/cli2ansible/settings.py` - Environment configuration

