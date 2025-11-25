"""Domain entities."""

from cli2ansible.domain.entities.cleaning import CleanedCommand, CleaningReport
from cli2ansible.domain.entities.command import Command
from cli2ansible.domain.entities.enums import SessionStatus, TaskConfidence
from cli2ansible.domain.entities.report import Report
from cli2ansible.domain.entities.role import Role
from cli2ansible.domain.entities.session import CastFile, Event, Session
from cli2ansible.domain.entities.task import Task

__all__ = [
    "SessionStatus",
    "TaskConfidence",
    "Session",
    "CastFile",
    "Event",
    "Command",
    "Task",
    "Role",
    "Report",
    "CleanedCommand",
    "CleaningReport",
]
