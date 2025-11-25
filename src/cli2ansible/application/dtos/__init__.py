"""Data Transfer Objects for application layer."""

from cli2ansible.application.dtos.clean_dto import (
    CleanedCommandResponseDTO,
    CleaningReportResponseDTO,
    CleanRequestDTO,
    CleanSessionResponseDTO,
)
from cli2ansible.application.dtos.compile_dto import CompileRequestDTO, CompileResponseDTO
from cli2ansible.application.dtos.event_dto import (
    EventCreateRequestDTO,
    EventResponseDTO,
    EventUpdateRequestDTO,
)
from cli2ansible.application.dtos.report_dto import ReportResponseDTO
from cli2ansible.application.dtos.session_dto import SessionCreateRequestDTO, SessionResponseDTO

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
