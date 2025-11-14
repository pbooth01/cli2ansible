"""Pydantic schemas for API."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SessionCreate(BaseModel):
    """Request schema for creating a session."""

    name: str = Field(..., min_length=1, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Response schema for session."""

    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    duration: float
    metadata: dict[str, Any]


class EventCreate(BaseModel):
    """Request schema for creating events."""

    timestamp: float
    event_type: str = Field(..., max_length=10)
    data: str = Field(..., max_length=10000)
    sequence: int = Field(default=0, ge=0)


class CompileRequest(BaseModel):
    """Request schema for compiling playbook."""

    pass  # No body needed for now


class MostCommonCommand(BaseModel):
    """Schema for most common command entry."""

    command: str
    count: int


class ReportResponse(BaseModel):
    """Response schema for translation report."""

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
    most_common_commands: list[MostCommonCommand]
    sudo_command_count: int


class ArtifactResponse(BaseModel):
    """Response schema for artifact."""

    artifact_url: str
    download_url: str


class CleanedCommandResponse(BaseModel):
    """Response schema for cleaned command."""

    command: str
    reason: str
    first_occurrence: float
    occurrence_count: int
    is_duplicate: bool
    is_error_correction: bool


class CleaningReportResponse(BaseModel):
    """Response schema for cleaning report."""

    session_id: UUID
    original_command_count: int
    cleaned_command_count: int
    duplicates_removed: int
    error_corrections_removed: int
    cleaning_rationale: str
    generated_at: datetime


class CleanSessionResponse(BaseModel):
    """Response schema for clean session operation."""

    cleaned_commands: list[CleanedCommandResponse]
    report: CleaningReportResponse


class EventResponse(BaseModel):
    """Response schema for event with ID and version."""

    id: UUID
    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int
    version: int


class CastUploadResponse(BaseModel):
    """Response schema for cast file upload."""

    status: str
    cast_file_key: str
    event_count: int
    events: list[EventResponse]


class EventsListResponse(BaseModel):
    """Response schema for list of events."""

    session_id: UUID
    event_count: int
    events: list[EventResponse]


class EventUpdateRequest(BaseModel):
    """Request schema for updating a single event."""

    version: int = Field(..., description="Current version for optimistic locking")
    timestamp: float | None = None
    data: str | None = None
    event_type: str | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str | None) -> str | None:
        """Validate event type."""
        if v and v not in ("i", "o", "x"):
            raise ValueError("event_type must be 'i', 'o', or 'x'")
        return v


class BatchEventUpdate(BaseModel):
    """Single event update in a batch request."""

    id: UUID = Field(..., description="Event ID to update")
    version: int = Field(..., description="Current version for optimistic locking")
    timestamp: float | None = None
    data: str | None = None
    event_type: str | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str | None) -> str | None:
        """Validate event type."""
        if v and v not in ("i", "o", "x"):
            raise ValueError("event_type must be 'i', 'o', or 'x'")
        return v


class BatchEventUpdateRequest(BaseModel):
    """Request schema for batch event updates."""

    updates: list[BatchEventUpdate] = Field(..., description="List of event updates", min_length=1)


class EventUpdateResult(BaseModel):
    """Result of a single event update in batch."""

    id: str
    status: Literal["success", "error"]
    event: EventResponse | None = None
    error: str | None = None


class BatchEventUpdateResponse(BaseModel):
    """Response schema for batch event updates."""

    updated: int = Field(..., description="Number of successfully updated events")
    failed: int = Field(..., description="Number of failed updates")
    results: list[EventUpdateResult]
