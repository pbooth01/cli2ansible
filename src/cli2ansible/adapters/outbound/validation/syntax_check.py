"""Validate generated playbooks with ansible-playbook --syntax-check."""

import subprocess
from dataclasses import dataclass

SYNTAX_CHECK_TIMEOUT_SECONDS = 60


@dataclass
class SyntaxCheckResult:
    """Outcome of a playbook syntax check."""

    is_valid: bool
    output: str


def check_playbook_syntax(playbook_path: str) -> SyntaxCheckResult:
    """Run ansible-playbook --syntax-check against a generated playbook."""
    completed = subprocess.run(
        ["ansible-playbook", "--syntax-check", "--", playbook_path],
        shell=False,
        capture_output=True,
        text=True,
        timeout=SYNTAX_CHECK_TIMEOUT_SECONDS,
    )
    return SyntaxCheckResult(
        is_valid=completed.returncode == 0,
        output=completed.stdout + completed.stderr,
    )
