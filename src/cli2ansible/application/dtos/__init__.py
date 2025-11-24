"""Data Transfer Objects for application layer."""

from cli2ansible.application.dtos.clean import (
    CleanedCommandResponseDTO,
    CleaningReportResponseDTO,
    CleanRequestDTO,
    CleanSessionResponseDTO,
)
from cli2ansible.application.dtos.compile import CompileRequestDTO, CompileResponseDTO
from cli2ansible.application.dtos.event import (
    EventCreateRequestDTO,
    EventResponseDTO,
    EventUpdateRequestDTO,
)
from cli2ansible.application.dtos.report import ReportResponseDTO
from cli2ansible.application.dtos.session import SessionCreateRequestDTO, SessionResponseDTO

__all__ = [
    # Session DTOs
    "SessionCreateRequestDTO",
    "SessionResponseDTO",
    # Event DTOs
    "EventCreateRequestDTO",
    "EventResponseDTO",
    "EventUpdateRequestDTO",
    # Compile DTOs
    "CompileRequestDTO",
    "CompileResponseDTO",
    # Clean DTOs
    "CleanRequestDTO",
    "CleanSessionResponseDTO",
    "CleanedCommandResponseDTO",
    "CleaningReportResponseDTO",
    # Report DTOs
    "ReportResponseDTO",
]
