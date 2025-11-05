"""Pydantic schemas for API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


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
