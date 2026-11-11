"""Unit tests for playbook syntax validation."""

import subprocess
from typing import Any

import pytest
from cli2ansible.adapters.outbound.validation import syntax_check


def _fake_run(returncode: int, stdout: str = "", stderr: str = "") -> Any:
    def _run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)

    return _run


def test_valid_playbook(monkeypatch: pytest.MonkeyPatch) -> None:
    """A zero exit code means the playbook is valid."""
    monkeypatch.setattr(syntax_check.subprocess, "run", _fake_run(0, stdout="playbook: site.yml"))
    result = syntax_check.check_playbook_syntax("site.yml")

    assert result.is_valid is True
    assert "site.yml" in result.output


def test_invalid_playbook(monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-zero exit code means the playbook is invalid."""
    monkeypatch.setattr(syntax_check.subprocess, "run", _fake_run(4, stderr="ERROR! bad indentation"))
    result = syntax_check.check_playbook_syntax("broken.yml")

    assert result.is_valid is False
    assert "bad indentation" in result.output

