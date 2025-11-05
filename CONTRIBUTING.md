# Contributing to cli2ansible

Thank you for your interest in contributing! This document outlines the development workflow and guidelines.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/cli2ansible.git
cd cli2ansible
make dev-install

# Start services
make docker-up

# Run tests
make test

# Format and lint
make format
make lint
```

## 📋 Development Workflow

### Branching Strategy

- `main` - Protected, production-ready code
- `release` - Integration branch for PRs
- Feature branches: `feat/<scope>-<short-name>`
- Bug fixes: `fix/<issue>-<short-name>`
- Docs: `docs/<topic>`

### Commit Style

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add systemctl translation rule
fix: handle missing session gracefully
docs: update API documentation
refactor: extract rule classes from rules_engine
test: add integration tests for compile service
chore: update dependencies
```

### Pull Request Process

1. **Create a branch** from `release`
2. **Make your changes** following coding conventions
3. **Write/update tests** - maintain or improve coverage
4. **Run checks locally**:
   ```bash
   make test
   make lint
   make type-check
   ```
5. **Update documentation** if needed
6. **Create PR** to `release` branch
7. **Address review feedback**

### PR Requirements

✅ All CI checks pass (tests, lint, type-check)
✅ At least 1 approving review
✅ No decrease in test coverage
✅ Documentation updated (if applicable)
✅ Conventional commit messages

### When to Use Agents

Use Claude Code agents to streamline your workflow:

#### TestAgent
Run **before** creating PR:
```text
Load prompts/agents/test-agent.yaml
Input: <paste git diff>
Generate test plan and test files.
```

#### SecurityAgent
Run **on PRs** touching:
- Authentication or authorization
- Secrets or credentials
- Network requests
- File operations
- Data storage

```text
Load prompts/agents/security-agent.yaml
Context: <describe auth model, data flow>
Input: <paste git diff>
```

#### RefactorAgent
Run when:
- File > 300 lines
- Function > 50 lines
- Complexity feels high

```text
Load prompts/agents/refactor-agent.yaml
Input: src/path/to/large_file.py
```

## 📐 Coding Conventions

See detailed conventions in [docs/conventions/](docs/conventions/):

- [General Code Style](docs/conventions/CODE_STYLE.md)
- [Python Conventions](docs/conventions/python.md)
- [Backend API](docs/conventions/backend_api.md)

### Key Principles

- **Hexagonal Architecture**: Domain logic separate from adapters
- **Type Safety**: All functions have type hints
- **Test Coverage**: New code should have tests
- **Clear Naming**: Descriptive names over comments
- **Small Functions**: Prefer <30 lines
- **No Secrets**: Use environment variables

## 🧪 Testing

### Test Structure

```
tests/
├── unit/           # Fast, isolated tests (domain logic)
├── integration/    # Adapter tests with real dependencies
└── api/            # HTTP endpoint tests
```

### Running Tests

```bash
# All tests with coverage
make test

# Specific test file
poetry run pytest tests/unit/test_translator.py

# Specific test
poetry run pytest tests/unit/test_translator.py::test_apt_install_translation

# With verbose output
poetry run pytest -v

# Stop on first failure
poetry run pytest -x
```

### Writing Tests

```python
# tests/unit/test_feature.py
def test_function_scenario_expected():
    """Test that function does X when Y."""
    # Arrange
    input_data = ...

    # Act
    result = function(input_data)

    # Assert
    assert result == expected
```

## 🏗️ Architecture

We follow **Hexagonal Architecture** (Ports & Adapters):

```
src/cli2ansible/
├── domain/              # Pure business logic (no I/O)
│   ├── models.py        # Domain entities
│   ├── ports.py         # Interfaces (contracts)
│   └── services.py      # Business logic
└── adapters/            # I/O implementations
    ├── inbound/         # Entry points (HTTP, CLI)
    └── outbound/        # External services (DB, S3)
```

**Rules:**
- Domain never imports from adapters
- Adapters implement ports (interfaces)
- Dependencies injected, not hardcoded

## 📝 Documentation

### When to Document

- New features: Update README, add PRD
- API changes: Update endpoint documentation
- Architecture decisions: Create ADR

### Creating PRDs

Use the template:

```bash
cp docs/prds/TEMPLATE.md docs/prds/2025-11-04-feature-name.md
# Edit and fill in sections
```

### Creating ADRs

```bash
cp docs/decisions/ADR-TEMPLATE.md docs/decisions/ADR-0003-decision-title.md
# Document your architectural decision
```

## 🔒 Security

### Security Checklist

Before submitting PR touching sensitive areas:

- [ ] No hardcoded secrets or credentials
- [ ] Input validation at all boundaries
- [ ] SQL/injection prevention
- [ ] Proper error handling (no info leakage)
- [ ] Dependencies scanned for CVEs
- [ ] Run SecurityAgent review

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email: security@yourproject.com (or your security contact)

## 🐛 Bug Reports

Use GitHub Issues with:

1. **Title**: Clear, specific description
2. **Environment**: Python version, OS, Docker
3. **Steps to reproduce**
4. **Expected behavior**
5. **Actual behavior**
6. **Logs/errors** (sanitize secrets!)

## 💡 Feature Requests

1. Check existing issues/PRDs
2. Create issue with:
   - Use case description
   - Proposed solution (optional)
   - Alternatives considered
3. Discuss before implementing large features

## 📚 Resources

- [Project README](README.md)
- [Coding Conventions](docs/conventions/)
- [Agent Prompts](prompts/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Poetry Docs](https://python-poetry.org/)

## ❓ Questions?

- Open a [GitHub Discussion](https://github.com/yourusername/cli2ansible/discussions)
- Join our [Slack/Discord] (if applicable)
- Check existing documentation first

## 🎉 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project README

Thank you for contributing! 🚀
