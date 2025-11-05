"""Domain models for cli2ansible."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class SessionStatus(str, Enum):
    """Session lifecycle status."""

    CREATED = "created"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    COMPILING = "compiling"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskConfidence(str, Enum):
    """Confidence level for translated tasks."""

    HIGH = "high"  # Direct module mapping
    MEDIUM = "medium"  # Shell with idempotency hints
    LOW = "low"  # Fallback shell task


@dataclass
class Session:
    """Terminal session recording."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    status: SessionStatus = SessionStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Terminal event from recording."""

    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int = 0


@dataclass
class Command:
    """Parsed command from terminal session."""

    session_id: UUID
    raw: str
    normalized: str
    cwd: str = "/"
    user: str = "root"
    sudo: bool = False
    timestamp: float = 0.0
    exit_code: int | None = None
    output: str = ""


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


@dataclass
class Role:
    """Ansible role structure."""

    name: str
    tasks: list[Task] = field(default_factory=list)
    handlers: list[Task] = field(default_factory=list)
    vars: dict[str, Any] = field(default_factory=dict)
    defaults: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    """Translation report with statistics and warnings."""

    session_id: UUID
    total_commands: int = 0
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    warnings: list[str] = field(default_factory=list)
    skipped_commands: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
