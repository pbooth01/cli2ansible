"""Unit tests for translator."""

from uuid import uuid4

import pytest
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.domain.entities import Command, TaskConfidence


@pytest.fixture()
def translator() -> RulesEngine:
    """Create translator instance."""
    return RulesEngine()


def test_apt_install_translation(translator: RulesEngine) -> None:
    """Test apt install command translation."""
    cmd = Command(
        session_id=uuid4(),
        raw="apt-get install -y nginx",
        normalized="apt-get install -y nginx",
        sudo=True,
    )
    task = translator.translate(cmd)

    assert task is not None
    assert task.module == "apt"
    assert task.args["name"] == ["nginx"]
    assert task.args["state"] == "present"
    assert task.confidence == TaskConfidence.HIGH
    assert task.become is True


@pytest.mark.parametrize(
    ("action", "state"),
    [("start", "started"), ("stop", "stopped"), ("restart", "restarted"), ("reload", "reloaded")],
)
@pytest.mark.parametrize("sudo", [False, True])
def test_systemctl_state_translation(
    translator: RulesEngine, action: str, state: str, sudo: bool
) -> None:
    """Translate service state actions while preserving privilege and source metadata."""
    normalized = f"systemctl {action} nginx.service"
    raw = f"sudo {normalized}" if sudo else normalized
    cmd = Command(session_id=uuid4(), raw=raw, normalized=normalized, sudo=sudo)
    task = translator.translate(cmd)

    assert task is not None
    assert task.name == f"{action.capitalize()} service: nginx.service"
    assert task.module == "systemd"
    assert task.args == {"name": "nginx.service", "state": state}
    assert task.confidence == TaskConfidence.HIGH
    assert task.become is sudo
    assert task.original_command == raw


@pytest.mark.parametrize("command", ["systemctl reload", "systemctl reload-or-restart nginx"])
def test_unsupported_systemctl_fallback(translator: RulesEngine, command: str) -> None:
    """Incomplete or unsupported actions must remain shell tasks."""
    cmd = Command(session_id=uuid4(), raw=command, normalized=command)
    task = translator.translate(cmd)

    assert task is not None
    assert task.module == "shell"
    assert task.args == {"cmd": command}
    assert task.confidence == TaskConfidence.LOW


def test_mkdir_translation(translator: RulesEngine) -> None:
    """Test mkdir command translation."""
    cmd = Command(
        session_id=uuid4(),
        raw="mkdir -p /var/www/html",
        normalized="mkdir -p /var/www/html",
    )
    task = translator.translate(cmd)

    assert task is not None
    assert task.module == "file"
    assert task.args["path"] == "/var/www/html"
    assert task.args["state"] == "directory"
    assert task.confidence == TaskConfidence.HIGH


def test_git_clone_translation(translator: RulesEngine) -> None:
    """Test git clone command translation."""
    cmd = Command(
        session_id=uuid4(),
        raw="git clone https://github.com/example/repo.git",
        normalized="git clone https://github.com/example/repo.git",
    )
    task = translator.translate(cmd)

    assert task is not None
    assert task.module == "git"
    assert task.args["repo"] == "https://github.com/example/repo.git"
    assert "dest" in task.args


def test_unknown_command_fallback(translator: RulesEngine) -> None:
    """Test fallback to shell module for unknown commands."""
    cmd = Command(
        session_id=uuid4(),
        raw="some-unknown-command --flag",
        normalized="some-unknown-command --flag",
    )
    task = translator.translate(cmd)

    assert task is not None
    assert task.module == "shell"
    assert task.args["cmd"] == "some-unknown-command --flag"
    assert task.confidence == TaskConfidence.LOW
