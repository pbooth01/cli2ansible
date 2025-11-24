"""Report-related DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ReportResponseDTO:
    """Response containing compilation report."""

    session_id: UUID
    total_commands: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    warnings: list[str]
    skipped_commands: list[str]
    generated_at: datetime
    module_breakdown: dict[str, int]
    high_confidence_percentage: float
    medium_confidence_percentage: float
    low_confidence_percentage: float
    session_duration_seconds: float
    most_common_commands: list[tuple[str, int]]
    sudo_command_count: int
