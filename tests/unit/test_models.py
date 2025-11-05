"""Unit tests for domain models."""

from cli2ansible.domain.models import Session, SessionStatus, Task, TaskConfidence


def test_session_creation() -> None:
    """Test creating a session."""
    session = Session(name="test-session")

    assert session.name == "test-session"
    assert session.status == SessionStatus.CREATED
    assert session.id is not None


def test_task_creation() -> None:
    """Test creating a task."""
    task = Task(
        name="Install nginx",
        module="apt",
        args={"name": "nginx", "state": "present"},
        confidence=TaskConfidence.HIGH,
    )

    assert task.name == "Install nginx"
    assert task.module == "apt"
    assert task.confidence == TaskConfidence.HIGH
    assert task.become is False
