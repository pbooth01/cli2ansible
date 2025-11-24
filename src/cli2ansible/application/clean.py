"""Application service for cleaning terminal sessions."""

from uuid import UUID

from cli2ansible.application.dtos import (
    CleanedCommandResponseDTO,
    CleaningReportResponseDTO,
    CleanSessionResponseDTO,
)
from cli2ansible.application.errors import BadRequestError, NotFoundError
from cli2ansible.application.ports import CleanSessionUseCase
from cli2ansible.domain.entities import CleanedCommand, CleaningReport, Command
from cli2ansible.domain.ports import LLMPort, SessionRepositoryPort
from cli2ansible.settings import settings


class CleanSessionService(CleanSessionUseCase):
    """Application service for cleaning terminal sessions.

    Encapsulates the use case logic for cleaning terminal sessions by removing
    duplicate and error correction commands using LLM analysis.
    """

    def __init__(self, repo: SessionRepositoryPort, llm: LLMPort) -> None:
        """Initialize clean service with ports."""
        self.repo = repo
        self.llm = llm

    def clean(self, session_id: UUID) -> CleanSessionResponseDTO:
        """Execute the clean use case: validate → extract → clean → return results.

        This is the main entry point that orchestrates the entire cleaning flow:
        1. Validates session exists
        2. Extracts commands from events if needed
        3. Validates command count is within limits
        4. Uses LLM to identify and remove duplicates/error corrections
        5. Returns cleaned commands with report

        Args:
            session_id: UUID of session to clean

        Returns:
            CleanSessionResponse with cleaned commands and cleaning report

        Raises:
            ValueError: If session not found, no commands, or command limit exceeded
        """
        from cli2ansible.application.ingest import IngestSessionService

        # Validate session exists
        session = self.repo.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        # Auto-extract commands if needed
        commands = self.repo.get_commands(session_id)
        if not commands:
            events = self.repo.get_events(session_id)
            if events:
                # Create temporary ingest service to extract commands
                ingest = IngestSessionService(self.repo)
                ingest.extract_commands(session_id)
                commands = self.repo.get_commands(session_id)

        # Validate we have commands
        if not commands:
            raise BadRequestError("No commands to clean. Session has no events or commands.")

        # Validate command count is within limits
        if len(commands) > settings.max_commands_for_cleaning:
            raise BadRequestError(
                f"Session has {len(commands)} commands, maximum {settings.max_commands_for_cleaning} allowed",
                {"command_count": len(commands), "max_allowed": settings.max_commands_for_cleaning},
            )

        # Clean using LLM
        cleaned_commands, report = self._clean_with_llm(commands, session_id)

        return CleanSessionResponseDTO(
            cleaned_commands=[self._cleaned_command_to_response(cmd) for cmd in cleaned_commands],
            report=self._report_to_response(report),
        )

    def _clean_with_llm(
        self, commands: list[Command], session_id: UUID
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """Use LLM to clean commands.

        Args:
            commands: List of commands to clean
            session_id: Session ID for report

        Returns:
            Tuple of (list[CleanedCommand], CleaningReport)
        """
        from cli2ansible.domain.entities import CleaningReport

        if not commands:
            # Return empty result
            empty_report = CleaningReport(
                session_id=session_id,
                original_command_count=0,
                cleaned_command_count=0,
                duplicates_removed=0,
                error_corrections_removed=0,
                cleaning_rationale="No commands found in session",
            )
            return [], empty_report

        return self.llm.clean_commands(commands, session_id)

    @staticmethod
    def _cleaned_command_to_response(cmd: CleanedCommand) -> CleanedCommandResponseDTO:
        """Convert cleaned command to response DTO."""
        return CleanedCommandResponseDTO(
            command=cmd.command,
            reason=cmd.reason,
            first_occurrence=cmd.first_occurrence,
            occurrence_count=cmd.occurrence_count,
            is_duplicate=cmd.is_duplicate,
            is_error_correction=cmd.is_error_correction,
        )

    @staticmethod
    def _report_to_response(report: CleaningReport) -> CleaningReportResponseDTO:
        """Convert cleaning report to response DTO."""
        return CleaningReportResponseDTO(
            session_id=report.session_id,
            original_command_count=report.original_command_count,
            cleaned_command_count=report.cleaned_command_count,
            duplicates_removed=report.duplicates_removed,
            error_corrections_removed=report.error_corrections_removed,
            cleaning_rationale=report.cleaning_rationale,
            generated_at=report.generated_at,
        )
