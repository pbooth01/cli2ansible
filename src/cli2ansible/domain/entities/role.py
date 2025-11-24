"""Role domain entity."""

from dataclasses import dataclass, field
from typing import Any

from cli2ansible.domain.entities.task import Task


@dataclass
class Role:
    """Ansible role structure."""

    name: str
    tasks: list[Task] = field(default_factory=list)
    handlers: list[Task] = field(default_factory=list)
    vars: dict[str, Any] = field(default_factory=dict)
    defaults: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
