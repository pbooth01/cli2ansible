# cli2ansible

**Turn manual terminal workflows into reproducible Ansible playbooks.**

[![CI Status](https://github.com/pbooth01/cli2ansible/workflows/ci/badge.svg)](https://github.com/pbooth01/cli2ansible/actions)
[![Code Coverage](https://codecov.io/gh/pbooth01/cli2ansible/graph/badge.svg)](https://codecov.io/gh/pbooth01/cli2ansible)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

`cli2ansible` is a service that captures terminal session recordings (e.g., from asciinema) and translates them into idempotent Ansible playbooks and roles. It enables DevOps engineers to convert ad-hoc command-line workflows into Infrastructure-as-Code (IaC).

### Key Features

- 📼 **Session Capture**: Upload terminal recordings (asciinema JSON format)
- 🔄 **Smart Translation**: Rule-based mapping from shell commands to Ansible modules
- 🎯 **Idempotency Detection**: Automatic `creates:`, `removes:`, and `changed_when:` hints
- 📦 **Artifact Generation**: Complete Ansible role with Molecule test scaffolding
- 🏗️ **Hexagonal Architecture**: Clean, testable, and maintainable codebase

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation) 1.7+
- Docker & Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/pbooth01/cli2ansible.git
cd cli2ansible

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
make dev-install

# Start services (PostgreSQL + MinIO + API)
make docker-up
```

### Usage

1. **Create a session:**
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "nginx-setup", "metadata": {}}'
```

2. **Upload terminal events:**
```bash
curl -X POST http://localhost:8000/sessions/{session_id}/events \
  -H "Content-Type: application/json" \
  -d '[{"timestamp": 1.0, "event_type": "o", "data": "apt-get install nginx\n", "sequence": 0}]'
```

3. **Compile to Ansible playbook:**
```bash
curl -X POST http://localhost:8000/sessions/{session_id}/compile
```

4. **Download artifact:**
```bash
curl http://localhost:8000/sessions/{session_id}/playbook -o role.zip
```

## 📁 Project Structure

```
cli2ansible/
├── src/cli2ansible/
│   ├── domain/                    # Core business logic (pure, no I/O)
│   │   ├── entities/              # Domain entities
│   │   ├── ports/                 # Port interfaces (contracts)
│   │   │   └── repositories/      # Repository ports
│   │   ├── services.py            # Domain services
│   │   ├── artifacts.py           # Role artifact exporter
│   │   └── exceptions.py          # Domain exceptions
│   ├── application/               # Application layer (use cases)
│   │   ├── ports/                 # Application use case interfaces
│   │   └── dtos/                  # Data transfer objects
│   ├── adapters/                  # Adapters (I/O implementations)
│   │   └── outbound/              # Outbound adapters
│   │       ├── db/                # Database adapters
│   │       ├── capture/           # Terminal capture adapters
│   │       ├── translator/        # Command translation adapters
│   │       ├── generators/        # Ansible role generators
│   │       ├── object_store/      # Object storage adapters
│   │       └── llm/               # LLM adapters
│   ├── api/                       # Inbound HTTP adapter
│   │   └── v1/                    # API v1 endpoints
│   ├── observability/             # Logging and monitoring
│   ├── app.py                     # Application composition root
│   ├── cli.py                     # CLI interface
│   └── settings.py                # Configuration
├── tests/                         # Unit, integration, and API tests
├── alembic/                       # Database migrations
├── docker-compose.yml             # Local development environment
└── pyproject.toml                 # Python dependencies
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run linting
make lint

# Run type checking
make type-check

# Format code
make format
```

## 🏗️ Architecture

This project follows **Hexagonal Architecture** (Ports & Adapters):

### Layers

1. **Domain Layer** (`domain/`)
   - Pure business logic with **no I/O dependencies**
   - **Entities**: Session, Event, Command, Task, Role, Report
   - **Ports**: Interface definitions for repositories, translators, storage, LLM
   - **Services**: Core business logic (IngestSession, CompilePlaybook, CleanSession)
   - **Artifacts**: Role artifact generation logic

2. **Application Layer** (`application/`)
   - Use case orchestration and coordination
   - **Services**: IngestSessionService, CompilePlaybookService, CleanSessionService
   - **DTOs**: Data transfer objects for API boundaries
   - **Ports**: Use case interfaces
   - Translates between domain entities and API representations

3. **Adapters Layer** (`adapters/`)
   - **Outbound Adapters** (external integrations):
     - `db/`: PostgreSQL repositories (SQLAlchemy)
     - `capture/`: Asciinema parser for terminal recordings
     - `translator/`: Rules engine for command-to-Ansible translation
     - `generators/`: Ansible role file generation
     - `object_store/`: S3/MinIO storage
     - `llm/`: Anthropic/OpenAI command cleaning

4. **API Layer** (`api/`)
   - **Inbound Adapter**: FastAPI HTTP endpoints
   - RESTful API with versioning (v1)
   - Request/response validation with Pydantic
   - Error handling and CORS middleware

### Dependency Flow

```
API (Inbound) → Application → Domain ← Adapters (Outbound)
                                ↑
                              Ports (Interfaces)
```

- Dependencies point **inward** toward the domain
- Domain has **zero** external dependencies
- All I/O happens in adapters
- Dependency injection configured in `app.py`

### Key Workflows

1. **Ingest Workflow**
   - Create session → Upload events/cast file → Parse commands
   - Domain service: `IngestSession`
   - Application service: `IngestSessionService`

2. **Compile Workflow**
   - Translate commands → Generate tasks → Create role → Export artifact
   - Domain service: `CompilePlaybook`
   - Application service: `CompilePlaybookService`

3. **Clean Workflow** (Optional)
   - Send commands to LLM → Get cleaned versions → Update session
   - Domain service: `CleanSession`
   - Application service: `CleanSessionService`

### Supported Commands

The rules engine currently supports:

- Package managers: `apt`, `yum`, `dnf`, `pip`, `npm`
- System services: `systemctl`
- File operations: `mkdir`, `cp`, `chown`, `chmod`
- Version control: `git clone`
- User management: `useradd`

Unknown commands fall back to the `shell` module.

## 🛠️ Development

### Running locally

```bash
# Start services
docker-compose up -d

# Run migrations
make migrate

# Run development server
poetry run uvicorn cli2ansible.app:app --reload
```

### Pre-commit hooks

```bash
# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

### Poetry Commands

```bash
# Add a new dependency
poetry add <package>

# Add a dev dependency
poetry add --group dev <package>

# Update dependencies
poetry update

# Generate/update poetry.lock
poetry lock

# Install with ansible tools (Linux/Docker only)
poetry install --with ansible
```

### Note on ansible-lint and molecule

These tools are **Linux-only** and won't install on macOS/Windows. They're in an optional group:
- On macOS/Windows: Use `make dev-install` (skips ansible tools)
- In Docker/Linux: They're automatically installed
- To test generated roles: Use Docker or CI/CD pipeline

### In Progress 🚧
- [ ] Frontend UI for session management
- [ ] Enhanced LLM translation for complex commands
- [ ] Real-time terminal monitoring

### Future 🔮
- [ ] Support for more package managers and tools
- [ ] Web UI for session management
- [ ] Multi-host playbook generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

All PRs must pass CI checks (tests + lint + type-check).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Testing with [Pytest](https://pytest.org/)
- Code quality with [Ruff](https://github.com/astral-sh/ruff) and [MyPy](https://mypy-lang.org/)

---

**Made with ❤️ for the DevOps community**
