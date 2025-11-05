# Python Conventions

## Version & Tools

- **Python**: >= 3.11
- **Package Manager**: Poetry
- **Formatter**: Black, Ruff
- **Type Checker**: MyPy (strict mode)
- **Testing**: Pytest with pytest-cov
- **Pre-commit**: All checks must pass

## Type Hints

```python
# Good: Explicit types
def translate_command(cmd: Command) -> Task | None:
    """Translate shell command to Ansible task."""
    ...

# Bad: No types
def translate_command(cmd):
    ...
```

- Use modern syntax: `list[str]` not `List[str]`
- Use `| None` instead of `Optional[]`
- Enable `strict = true` in mypy config

## Naming

- **Classes**: PascalCase (`SessionRepository`)
- **Functions/Variables**: snake_case (`create_session`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)
- **Private**: Single underscore prefix (`_internal_method`)
- **Type aliases**: PascalCase (`TaskList = list[Task]`)

## Imports

```python
# Order: stdlib -> third-party -> local
import re
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from cli2ansible.domain.models import Session
```

- Use absolute imports from `src/`
- Group imports logically
- Ruff will auto-sort

## Dataclasses & Pydantic

```python
# Domain models: dataclasses
@dataclass
class Command:
    session_id: UUID
    raw: str
    sudo: bool = False

# API schemas: Pydantic
class SessionCreate(BaseModel):
    name: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Error Handling

```python
# Domain exceptions
class SessionNotFoundError(ValueError):
    """Raised when session doesn't exist."""
    def __init__(self, session_id: UUID):
        super().__init__(f"Session {session_id} not found")

# Usage
def get_session(session_id: UUID) -> Session:
    session = repo.get(session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    return session
```

## Testing

```python
# Test naming: test_<function>_<scenario>
def test_translate_apt_install_returns_apt_task():
    """Test that apt install commands map to apt module."""
    cmd = Command(...)
    task = translator.translate(cmd)

    assert task.module == "apt"
    assert task.confidence == TaskConfidence.HIGH

# Use fixtures from conftest.py
def test_session_creation(repository: SQLAlchemyRepository):
    session = repository.create(Session(name="test"))
    assert session.id is not None
```

## Async/Await

- Avoid mixing sync/async in same module
- Use `async def` only when truly needed
- FastAPI endpoints can be sync if no I/O

## Documentation

```python
def compile_playbook(session_id: UUID) -> tuple[Role, Report]:
    """Compile session commands into Ansible role.

    Args:
        session_id: ID of the session to compile

    Returns:
        Tuple of (generated role, translation report)

    Raises:
        SessionNotFoundError: If session doesn't exist

    Example:
        >>> role, report = compiler.compile_playbook(session_id)
        >>> print(f"Generated {len(role.tasks)} tasks")
    """
```

## Anti-patterns to Avoid

❌ **Mutable default arguments**
```python
def bad(items=[]):  # Bug: shared state
    items.append(1)
```

❌ **Bare except**
```python
try:
    risky_operation()
except:  # Catches KeyboardInterrupt, SystemExit!
    pass
```

❌ **God classes**
```python
class Everything:  # Does too much
    def create_session(self): ...
    def compile_playbook(self): ...
    def send_email(self): ...
```

❌ **String-based imports**
```python
module = __import__("some.module")  # Hard to track
```

## Best Practices

✅ **Use context managers**
```python
with open(path) as f:
    data = f.read()
```

✅ **Comprehensions over loops**
```python
# Good
task_names = [t.name for t in tasks if t.confidence == TaskConfidence.HIGH]

# Acceptable
task_names = []
for task in tasks:
    if task.confidence == TaskConfidence.HIGH:
        task_names.append(task.name)
```

✅ **Dependency injection**
```python
class CompilePlaybook:
    def __init__(
        self,
        repo: SessionRepositoryPort,
        translator: TranslatorPort,
    ):
        self.repo = repo
        self.translator = translator
```
