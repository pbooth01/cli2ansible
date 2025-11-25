"""Enums for domain entities."""

from enum import Enum


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
