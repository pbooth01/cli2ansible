"""Cleaning domain entities."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class CleanedCommand:
    """A command that has been cleaned and deduplicated."""

    session_id: UUID
    command: str
    reason: str
    first_occurrence: float
    occurrence_count: int = 1
    is_duplicate: bool = False
    is_error_correction: bool = False


@dataclass
class CleaningReport:
    """Report of terminal session cleaning."""

    session_id: UUID
    original_command_count: int
    cleaned_command_count: int
    duplicates_removed: int
    error_corrections_removed: int
    cleaning_rationale: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
