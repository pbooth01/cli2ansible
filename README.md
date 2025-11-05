# cli2ansible

**Turn manual terminal workflows into reproducible Ansible playbooks.**

![CI Status](https://github.com/yourusername/cli2ansible/workflows/ci/badge.svg)
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
git clone https://github.com/yourusername/cli2ansible.git
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
│   ├── domain/              # Core business logic
│   │   ├── models.py        # Domain entities
│   │   ├── ports.py         # Port interfaces
│   │   └── services.py      # Domain services
│   ├── adapters/
│   │   ├── inbound/http/    # FastAPI REST API
│   │   └── outbound/        # Database, S3, translators
│   └── app.py               # Application composition root
├── tests/                   # Unit, integration, and API tests
├── alembic/                 # Database migrations
├── docker-compose.yml       # Local development environment
└── pyproject.toml           # Python dependencies
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

- **Domain Layer**: Pure business logic (models, services, ports)
- **Adapters**:
  - Inbound: FastAPI HTTP endpoints
  - Outbound: PostgreSQL, S3/MinIO, Ansible generators
- **Application**: Dependency wiring and composition root

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

## 📈 Roadmap

- [ ] Real-time terminal monitoring (Phase 2)
- [ ] LLM-assisted translation for complex commands
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
