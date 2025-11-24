"""Report domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


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
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    module_breakdown: dict[str, int] = field(default_factory=dict)
    high_confidence_percentage: float = 0.0
    medium_confidence_percentage: float = 0.0
    low_confidence_percentage: float = 0.0
    session_duration_seconds: float = 0.0
    most_common_commands: list[tuple[str, int]] = field(default_factory=list)
    sudo_command_count: int = 0
