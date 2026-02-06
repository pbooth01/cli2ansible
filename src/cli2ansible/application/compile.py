"""Application service for compiling sessions to Ansible playbooks."""

from uuid import UUID

from cli2ansible.application.dtos import CompileResponseDTO
from cli2ansible.application.errors import NotFoundError
from cli2ansible.application.ports import CompilePlaybookUseCase
from cli2ansible.domain.artifacts import RoleArtifactExporter
from cli2ansible.domain.entities import Report, Role, SessionStatus, TaskConfidence
from cli2ansible.domain.ports import (
    ObjectStorePort,
    RoleGeneratorPort,
    SessionRepositoryPort,
    TranslatorPort,
)


class CompilePlaybookService(CompilePlaybookUseCase):
    """Application service for compiling sessions to Ansible playbooks.

    Encapsulates the use case logic for compiling terminal sessions into
    Ansible playbooks, handling extraction, compilation, and artifact export.
    """

    def __init__(
        self,
        repo: SessionRepositoryPort,
        translator: TranslatorPort,
        generator: RoleGeneratorPort,
        store: ObjectStorePort,
    ) -> None:
        """Initialize compile service with ports."""
        self.repo = repo
        self.translator = translator
        self.generator = generator
        self.store = store
        self.artifact_exporter = RoleArtifactExporter(generator, store)

    def compile(self, session_id: UUID) -> CompileResponseDTO:
        """Execute the compile use case: extract → compile → export → return URL.

        This is the main entry point that orchestrates the entire compilation flow:
        1. Validates session exists
        2. Extracts commands from events if needed
        3. Compiles commands to Ansible role
        4. Exports role artifact to storage
        5. Generates download URL

        Args:
            session_id: UUID of session to compile

        Returns:
            CompileResponse with artifact and download URLs

        Raises:
            ValueError: If session not found or compilation fails
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

        # Compile to role
        role, _ = self._compile_to_role(session_id)

        # Export artifact
        artifact_key = self.artifact_exporter.export(role, session_id)

        # Generate download URL
        download_url = self.store.generate_url(artifact_key)

        return CompileResponseDTO(
            artifact_url=artifact_key,
            download_url=download_url,
        )

    def _compile_to_role(self, session_id: UUID) -> tuple[Role, Report]:
        """Compile session commands into Ansible role (internal helper method).

        Args:
            session_id: UUID of session to compile

        Returns:
            Tuple of (Role, Report) with compilation results
        """
        from collections import Counter

        session = self.repo.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        session.status = SessionStatus.COMPILING
        self.repo.update(session)

        commands = self.repo.get_commands(session_id)
        tasks = []
        report = Report(session_id=session_id, total_commands=len(commands))

        # Track module usage
        module_counts: dict[str, int] = {}

        for command in commands:
            task = self.translator.translate(command)
            if task:
                tasks.append(task)
                if task.confidence == TaskConfidence.HIGH:
                    report.high_confidence += 1
                elif task.confidence == TaskConfidence.MEDIUM:
                    report.medium_confidence += 1
                else:
                    report.low_confidence += 1

                # Track module usage
                module_counts[task.module] = module_counts.get(task.module, 0) + 1
            else:
                report.skipped_commands.append(command.raw)

        # Calculate percentages
        if report.total_commands > 0:
            report.high_confidence_percentage = (
                report.high_confidence / report.total_commands
            ) * 100
            report.medium_confidence_percentage = (
                report.medium_confidence / report.total_commands
            ) * 100
            report.low_confidence_percentage = (
                report.low_confidence / report.total_commands
            ) * 100

        # Calculate session duration
        if commands:
            timestamps = [cmd.timestamp for cmd in commands]
            report.session_duration_seconds = max(timestamps) - min(timestamps)

        # Calculate most common commands (top 5)
        command_counter = Counter(cmd.normalized for cmd in commands)
        report.most_common_commands = command_counter.most_common(5)

        # Count sudo commands
        report.sudo_command_count = sum(1 for cmd in commands if cmd.sudo)

        # Set module breakdown
        report.module_breakdown = module_counts

        role = Role(name=session.name or f"role_{session_id}", tasks=tasks)

        session.status = SessionStatus.COMPLETED
        self.repo.update(session)

        return role, report

    def export_artifact(self, role: Role, session_id: UUID) -> str:
        """Export role artifact and return artifact key (for backward compatibility with API)."""
        return self.artifact_exporter.export(role, session_id)

    def get_report(self, session_id: UUID) -> Report:
        """Get translation report for a session."""
        from cli2ansible.application.ingest import IngestSessionService

        session = self.repo.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        # Auto-extract commands if not already done
        commands = self.repo.get_commands(session_id)
        if not commands:
            events = self.repo.get_events(session_id)
            if events:
                # Need to extract commands - create a temporary IngestSessionService
                ingest = IngestSessionService(self.repo)
                ingest.extract_commands(session_id)
                commands = self.repo.get_commands(session_id)

        # Re-compile to get report
        from collections import Counter

        report = Report(session_id=session_id, total_commands=len(commands))
        module_counts: dict[str, int] = {}

        for command in commands:
            task = self.translator.translate(command)
            if task:
                if task.confidence == TaskConfidence.HIGH:
                    report.high_confidence += 1
                elif task.confidence == TaskConfidence.MEDIUM:
                    report.medium_confidence += 1
                else:
                    report.low_confidence += 1
                module_counts[task.module] = module_counts.get(task.module, 0) + 1
            else:
                report.skipped_commands.append(command.raw)

        # Calculate percentages
        if report.total_commands > 0:
            report.high_confidence_percentage = (
                report.high_confidence / report.total_commands
            ) * 100
            report.medium_confidence_percentage = (
                report.medium_confidence / report.total_commands
            ) * 100
            report.low_confidence_percentage = (
                report.low_confidence / report.total_commands
            ) * 100

        # Calculate session duration
        if commands:
            timestamps = [cmd.timestamp for cmd in commands]
            report.session_duration_seconds = max(timestamps) - min(timestamps)

        # Calculate most common commands
        command_counter = Counter(cmd.normalized for cmd in commands)
        report.most_common_commands = command_counter.most_common(5)

        # Count sudo commands
        report.sudo_command_count = sum(1 for cmd in commands if cmd.sudo)

        # Set module breakdown
        report.module_breakdown = module_counts

        return report
