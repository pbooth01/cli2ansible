"""Cleaning-related DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CleanRequestDTO:
    """Request to clean a session."""

    pass  # No specific fields needed, session_id comes from URL


@dataclass
class CleanedCommandResponseDTO:
    """Response containing a cleaned command."""

    command: str
    reason: str
    first_occurrence: float
    occurrence_count: int
    is_duplicate: bool
    is_error_correction: bool


@dataclass
class CleaningReportResponseDTO:
    """Response containing cleaning report information."""

    session_id: UUID
    original_command_count: int
    cleaned_command_count: int
    duplicates_removed: int
    error_corrections_removed: int
    cleaning_rationale: str
    generated_at: datetime


@dataclass
class CleanSessionResponseDTO:
    """Response from cleaning a session."""

    cleaned_commands: list[CleanedCommandResponseDTO]
    report: CleaningReportResponseDTO
