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
    event_type: str
    data: str
    sequence: int = 0


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
