# Testing Rules

## Overview
These rules ensure adequate test coverage and quality for all code changes.

## Rules

### 1. Minimum Test Coverage
- **Severity**: Critical
- **Description**: All code changes must maintain ≥80% test coverage
- **Requirements**:
  - Overall project coverage ≥ 80%
  - New code coverage ≥ 80%
  - Critical paths have 100% coverage
  - Run `poetry run pytest --cov` to verify

### 2. Unit Tests Required
- **Severity**: Critical
- **Description**: All domain logic must have unit tests
- **Requirements**:
  - Test all public methods in domain classes
  - Test business logic thoroughly
  - Use mocks for external dependencies
  - Tests should be fast (<100ms each)
  - Follow AAA pattern (Arrange, Act, Assert)

**Example**:
```python
def test_compile_playbook_success():
    # Arrange
    session = Session(id=uuid4(), name="test", commands=["ls -la"])
    compiler = CompilePlaybook()

    # Act
    result = compiler.compile(session)

    # Assert
    assert result.success is True
    assert "tasks:" in result.playbook_yaml
```

### 3. Integration Tests Required
- **Severity**: Critical
- **Description**: All adapters must have integration tests
- **Requirements**:
  - Test database adapters with real DB
  - Test HTTP adapters with test client
  - Test external service integrations
  - Use fixtures for test data
  - Clean up after tests

**Example**:
```python
@pytest.mark.integration
def test_create_session_endpoint(client: TestClient, db: Session):
    # Arrange
    request_data = {
        "name": "test-session",
        "commands": ["echo hello"]
    }

    # Act
    response = client.post("/api/sessions", json=request_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "test-session"
```

### 4. Edge Cases Covered
- **Severity**: Critical
- **Description**: Tests must cover edge cases and error conditions
- **Test scenarios**:
  - Empty inputs
  - Null/None values
  - Maximum/minimum values
  - Invalid data types
  - Concurrent operations
  - Network failures
  - Database errors

**Example**:
```python
def test_compile_playbook_empty_commands():
    session = Session(id=uuid4(), name="test", commands=[])
    compiler = CompilePlaybook()

    with pytest.raises(ValueError, match="No commands"):
        compiler.compile(session)

def test_compile_playbook_invalid_command():
    session = Session(id=uuid4(), name="test", commands=[""])
    compiler = CompilePlaybook()

    result = compiler.compile(session)
    assert result.success is False
```

### 5. Test Organization
- **Severity**: Warning
- **Description**: Tests must be well-organized and maintainable
- **Requirements**:
  - Mirror source code structure in tests/
  - One test file per source file
  - Group related tests in classes
  - Use descriptive test names
  - Use fixtures for common setup

**Structure**:
```
tests/
├── unit/
│   ├── domain/
│   │   └── test_session.py
│   └── services/
│       └── test_compile_playbook.py
└── integration/
    ├── adapters/
    │   └── test_session_repository.py
    └── http/
        └── test_api.py
```

### 6. Test Quality
- **Severity**: Warning
- **Description**: Tests must be reliable and maintainable
- **Requirements**:
  - No flaky tests
  - No test interdependencies
  - Clear assertion messages
  - Test one thing per test
  - Use parametrize for similar tests

**Example**:
```python
@pytest.mark.parametrize("command,expected", [
    ("ls -la", True),
    ("cd /tmp", True),
    ("sudo rm -rf /", False),
])
def test_command_validation(command: str, expected: bool):
    result = validate_command(command)
    assert result == expected, f"Command '{command}' validation failed"
```

## Test Types

### Unit Tests
- Test individual functions/methods in isolation
- Mock all external dependencies
- Fast execution (<100ms)
- Located in `tests/unit/`

### Integration Tests
- Test component interactions
- Use real databases/services
- Slower execution (acceptable)
- Located in `tests/integration/`

### API Tests
- Test HTTP endpoints end-to-end
- Use TestClient
- Verify request/response formats
- Located in `tests/integration/http/`

## Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=src/cli2ansible --cov-report=term-missing

# Unit tests only
poetry run pytest tests/unit

# Integration tests only
poetry run pytest tests/integration

# Specific test
poetry run pytest tests/unit/domain/test_session.py::test_session_creation
```

## Enforcement
- PRs without adequate tests are blocked
- Coverage must not decrease
- All tests must pass before merge
- Flaky tests must be fixed immediately
