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



def test_playbook_path_is_passed_as_single_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    """Shell metacharacters in the path must never reach a shell."""
    captured: dict[str, Any] = {}

    def _run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(syntax_check.subprocess, "run", _run)
    malicious_path = "site.yml; touch /tmp/pwned"
    syntax_check.check_playbook_syntax(malicious_path)

    command = captured["args"][0]
    assert command == ["ansible-playbook", "--syntax-check", "--", malicious_path]
    assert captured["kwargs"].get("shell") is False
