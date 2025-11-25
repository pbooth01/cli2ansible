"""Task domain entity."""

from dataclasses import dataclass, field
from typing import Any

from cli2ansible.domain.entities.enums import TaskConfidence


@dataclass
class Task:
    """Ansible task representation."""

    name: str
    module: str
    args: dict[str, Any] = field(default_factory=dict)
    confidence: TaskConfidence = TaskConfidence.LOW
    original_command: str = ""
    changed_when: str | None = None
    creates: str | None = None
    removes: str | None = None
    become: bool = False
    tags: list[str] = field(default_factory=list)
