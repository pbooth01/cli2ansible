# Feature Implementation Workflow

Complete workflow for implementing features with Augment Agent from PRD to merged PR.

## Overview

This workflow guides Augment Agent through:
1. Understanding requirements from PRD or feature description
2. Planning implementation with task breakdown
3. Writing code following project conventions
4. Creating comprehensive tests
5. Running quality checks
6. Creating and managing PR

## Usage

### With Existing PRD

```
Implement the feature described in docs/prds/<feature-name>.md
```

### With Feature Description

```
Implement a new feature: <description>

Follow the workflow in .augment/workflows/implement-feature.md
```

## Workflow Steps

### Step 1: Requirements Analysis
- Read and understand the PRD or feature description
- Identify affected components and files
- List dependencies and integration points
- Create implementation plan using tasklist

### Step 2: Branch Management
```bash
# Create feature branch
git checkout -b feature/<descriptive-name>

# Target merge branch: release-<version> (from VERSION file)
```

### Step 3: Implementation
Follow hexagonal architecture:
- **Domain logic**: `src/cli2ansible/domain/`
  - Pure business logic, no I/O
  - Use dependency injection
  - Return domain models

- **Ports**: `src/cli2ansible/domain/ports.py`
  - Define interfaces for adapters
  - Use Protocol or ABC

- **Adapters**: `src/cli2ansible/adapters/`
  - Inbound: HTTP API, CLI
  - Outbound: Database, S3, external services

**Key Principles**:
- Keep changes focused and atomic
- Follow existing patterns in codebase
- Maintain type safety with type hints
- Write self-documenting code
- Handle errors gracefully

### Step 4: Testing
Generate comprehensive tests:

**Unit Tests** (`tests/unit/`)
- Test domain logic in isolation
- Mock all adapters and external dependencies
- Cover edge cases and error conditions
- Aim for 100% coverage of domain logic

**Integration Tests** (`tests/integration/`)
- Test adapter implementations
- Use real database (test fixtures)
- Test service interactions

**API Tests** (`tests/api/`)
- Test HTTP endpoints
- Verify request/response schemas
- Test error responses

**Test Checklist**:
- [ ] Unit tests for all new domain logic
- [ ] Integration tests for adapters
- [ ] API tests for new endpoints
- [ ] Edge cases covered
- [ ] Error conditions tested
- [ ] All tests passing locally

### Step 5: Quality Checks
Run all checks in this exact order:

```bash
# 1. Format code
make format

# 2. Lint code
make lint

# 3. Type check
make type-check

# 4. Run tests with coverage
make test
```

**All checks must pass before proceeding.**

If any check fails:
1. Fix the issues
2. Re-run ALL checks from the beginning
3. Do not proceed until everything passes

### Step 6: Documentation
Update documentation if needed:

- [ ] Docstrings for public functions/classes
- [ ] Update README if user-facing changes
- [ ] Update API documentation
- [ ] Add/update architecture diagrams if needed
- [ ] Update CHANGELOG.md

### Step 7: Security Review
Check for security issues:

- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] Command injection prevention
- [ ] Path traversal prevention
- [ ] Proper authentication/authorization

### Step 8: Commit
```bash
git add .
git commit -m "<type>: <concise description>

<detailed explanation of changes>

🤖 Generated with Augment Agent"
```

**Commit types**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### Step 9: Push
```bash
git push -u origin <branch-name>
```

### Step 10: Create PR
```bash
gh pr create --title "<feature-title>" \
  --body "$(cat <<'EOF'
## Summary
<Brief description of the feature>

## Changes
- <List of key changes>
- <File modifications>

## Test Plan
- [x] Unit tests added/updated
- [x] Integration tests added/updated
- [x] All tests passing (make test)
- [x] Code coverage maintained/improved

## Quality Checks
- [x] Code formatted (make format)
- [x] Lint checks passing (make lint)
- [x] Type checks passing (make type-check)
- [x] Security review completed

## Documentation
- [ ] Docstrings added/updated
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)

🤖 Generated with Augment Agent
EOF
)" \
  --base release-<version>
```

## Project Context

### Stack
- **Language**: Python 3.11+
- **Package Manager**: Poetry
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Storage**: S3/MinIO
- **Testing**: pytest
- **Linting**: ruff + mypy
- **Formatting**: black + ruff

### Architecture
Hexagonal (ports & adapters):
- **Domain**: Pure business logic
- **Ports**: Interfaces for adapters
- **Adapters Inbound**: HTTP API, CLI
- **Adapters Outbound**: Database, S3, translators

### Conventions
- Follow `docs/conventions/CODE_STYLE.md`
- Use type hints everywhere
- Write docstrings for public APIs
- Keep functions small and focused
- Prefer composition over inheritance

## Error Handling

If any step fails:
1. Analyze the failure
2. Fix the issue
3. Retry from the failed step
4. Do not skip steps
5. Do not mark incomplete work as done

## Next Steps After PR Creation

1. CI will run automatically
2. Auto-merge workflow will enable merge if CI passes
3. PR will merge automatically (if approvals met)
4. Monitor for any issues post-merge
