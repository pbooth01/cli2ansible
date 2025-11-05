# Unit Test Harness

Standard patterns for writing unit tests in cli2ansible.

## Test Framework

- **Pytest** for all tests
- **Fixtures** in `tests/conftest.py` for shared dependencies
- **Factory pattern** for test data creation
- **Mocks** for external dependencies (use `unittest.mock` or `pytest-mock`)

## Test Structure

```python
def test_<function_name>_<scenario>_<expected_result>():
    """Clear description of what this test verifies.

    Explain WHY we're testing this if not obvious.
    """
    # Arrange: Set up test data and dependencies
    input_data = create_test_data()
    mock_dependency = Mock()

    # Act: Execute the code under test
    result = function_under_test(input_data, mock_dependency)

    # Assert: Verify the expected outcome
    assert result == expected_value
    mock_dependency.method.assert_called_once()
```

## Domain Model Tests

Test pure business logic without I/O:

```python
from cli2ansible.domain.models import Session, SessionStatus

def test_session_creation_sets_default_status():
    """Test that new sessions start with CREATED status."""
    session = Session(name="test-session")

    assert session.status == SessionStatus.CREATED
    assert session.id is not None


def test_session_name_is_required():
    """Test that session name cannot be empty."""
    with pytest.raises(ValueError):
        Session(name="")
```

## Service Tests

Test business logic with mocked ports:

```python
from unittest.mock import Mock
from cli2ansible.domain.services import IngestSession

def test_create_session_saves_to_repository():
    """Test that create_session persists the session."""
    # Arrange
    mock_repo = Mock()
    mock_repo.create.return_value = Session(id=uuid4(), name="test")
    service = IngestSession(mock_repo)

    # Act
    result = service.create_session("test-session")

    # Assert
    assert result.name == "test"
    mock_repo.create.assert_called_once()
```

## Adapter Tests (Integration)

Test adapters with real dependencies (use in-memory/test versions):

```python
def test_repository_saves_and_retrieves_session():
    """Test SQLAlchemy repository persists sessions."""
    # Use in-memory SQLite
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()

    # Create session
    session = Session(name="test-session")
    saved = repo.create(session)

    # Retrieve and verify
    retrieved = repo.get(saved.id)
    assert retrieved is not None
    assert retrieved.name == "test-session"
```

## API Tests

Test HTTP endpoints end-to-end:

```python
from fastapi.testclient import TestClient

def test_create_session_returns_201():
    """Test POST /sessions creates session and returns 201."""
    client = TestClient(app)

    response = client.post(
        "/sessions",
        json={"name": "test-session", "metadata": {}}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert "id" in data
```

## Test Data Factories

Create reusable test data builders:

```python
# tests/factories.py
def create_command(
    session_id: UUID | None = None,
    raw: str = "apt-get install nginx",
    sudo: bool = False,
) -> Command:
    """Factory for creating test commands."""
    return Command(
        session_id=session_id or uuid4(),
        raw=raw,
        normalized=raw.strip(),
        sudo=sudo,
        timestamp=time.time(),
    )


# Usage in tests
def test_translator_with_sudo_command():
    cmd = create_command(raw="sudo apt-get install nginx", sudo=True)
    task = translator.translate(cmd)
    assert task.become is True
```

## Parameterized Tests

Test multiple scenarios efficiently:

```python
import pytest

@pytest.mark.parametrize("input_cmd,expected_module", [
    ("apt-get install nginx", "apt"),
    ("yum install nginx", "yum"),
    ("dnf install nginx", "dnf"),
])
def test_package_manager_translation(input_cmd, expected_module):
    """Test that package managers translate to correct modules."""
    cmd = create_command(raw=input_cmd)
    task = translator.translate(cmd)

    assert task.module == expected_module
```

## Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async endpoint behavior."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/sessions")
        assert response.status_code == 200
```

## Fixtures

Reusable test dependencies:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def in_memory_db():
    """Provide in-memory SQLite database."""
    return "sqlite:///:memory:"

@pytest.fixture
def repository(in_memory_db):
    """Provide configured repository."""
    repo = SQLAlchemyRepository(in_memory_db)
    repo.create_tables()
    return repo

@pytest.fixture
def translator():
    """Provide rules engine translator."""
    return RulesEngine()


# Usage in test
def test_with_fixtures(repository, translator):
    """Test using fixtures."""
    # repository and translator are automatically injected
    ...
```

## Anti-patterns to Avoid

❌ **Testing implementation details**
```python
# Bad: Testing internal state
def test_bad():
    service._internal_cache == {}  # Don't test private attributes
```

❌ **Overly complex test setup**
```python
# Bad: Test is harder to understand than the code
def test_bad():
    # 50 lines of setup...
    result = function()
    assert result
```

❌ **Testing multiple things in one test**
```python
# Bad: Test does too much
def test_bad():
    # Tests creation, update, deletion, and querying
    ...
```

❌ **Mocking too much**
```python
# Bad: Everything is mocked, testing nothing
def test_bad():
    mock1 = Mock()
    mock2 = Mock()
    mock3 = Mock()
    # What are we actually testing?
```

## Best Practices

✅ **One assertion per test (or closely related assertions)**
✅ **Clear test names that describe the scenario**
✅ **Arrange-Act-Assert structure**
✅ **Test edge cases and error conditions**
✅ **Keep tests fast (<100ms for unit tests)**
✅ **Use fixtures for shared setup**
✅ **Mock external dependencies (network, file system)**

## Coverage Goals

- **Domain layer**: 90%+ (critical business logic)
- **Services**: 85%+ (orchestration logic)
- **Adapters**: 75%+ (I/O implementations)
- **API**: 80%+ (endpoint tests)

## Running Tests

```bash
# All tests
make test

# With coverage report
poetry run pytest --cov=src --cov-report=html

# Specific test file
poetry run pytest tests/unit/test_translator.py

# Specific test
poetry run pytest tests/unit/test_translator.py::test_apt_install

# Stop on first failure
poetry run pytest -x

# Verbose output
poetry run pytest -v

# Show print statements
poetry run pytest -s
```
