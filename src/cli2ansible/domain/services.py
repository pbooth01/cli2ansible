"""Domain services (business logic)."""
import re
from typing import Any
from uuid import UUID

from cli2ansible.domain.models import (
    Command,
    Event,
    Report,
    Role,
    Session,
    SessionStatus,
    Task,
    TaskConfidence,
)
from cli2ansible.domain.ports import (
    ObjectStorePort,
    RoleGeneratorPort,
    SessionRepositoryPort,
    TranslatorPort,
)


class IngestSession:
    """Service for ingesting terminal sessions."""

    def __init__(self, repo: SessionRepositoryPort) -> None:
        self.repo = repo

    def create_session(self, name: str, metadata: dict[str, Any] | None = None) -> Session:
        """Create a new session."""
        session = Session(name=name, metadata=metadata or {})
        return self.repo.create(session)

    def save_events(self, session_id: UUID, events: list[Event]) -> None:
        """Save events for a session."""
        session = self.repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = SessionStatus.UPLOADED
        self.repo.update(session)
        self.repo.save_events(events)

    def extract_commands(self, session_id: UUID) -> list[Command]:
        """Extract commands from session events."""
        events = self.repo.get_events(session_id)
        commands: list[Command] = []

        current_line = ""
        for event in events:
            if event.event_type == "o":  # Output
                current_line += event.data
                if "\n" in current_line or "\r" in current_line:
                    lines = current_line.split("\n")
                    for line in lines[:-1]:
                        cmd = self._parse_command_line(line, session_id, event.timestamp)
                        if cmd:
                            commands.append(cmd)
                    current_line = lines[-1]

        self.repo.save_commands(commands)
        return commands

    def _parse_command_line(self, line: str, session_id: UUID, timestamp: float) -> Command | None:
        """Parse a line to extract command."""
        # Remove ANSI escape codes
        line = re.sub(r"\x1b\[[0-9;]*m", "", line)
        line = line.strip()

        # Skip empty lines and prompts
        if not line or line.endswith("$") or line.endswith("#"):
            return None

        # Detect sudo
        sudo = line.startswith("sudo ")
        if sudo:
            line = line[5:]

        return Command(
            session_id=session_id,
            raw=line,
            normalized=line.strip(),
            sudo=sudo,
            timestamp=timestamp,
        )


class CompilePlaybook:
    """Service for compiling commands into playbooks."""

    def __init__(
        self,
        repo: SessionRepositoryPort,
        translator: TranslatorPort,
        generator: RoleGeneratorPort,
        store: ObjectStorePort,
    ) -> None:
        self.repo = repo
        self.translator = translator
        self.generator = generator
        self.store = store

    def compile(self, session_id: UUID) -> tuple[Role, Report]:
        """Compile session commands into an Ansible role."""
        session = self.repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = SessionStatus.COMPILING
        self.repo.update(session)

        commands = self.repo.get_commands(session_id)
        tasks: list[Task] = []
        report = Report(session_id=session_id, total_commands=len(commands))

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
            else:
                report.skipped_commands.append(command.raw)

        role = Role(name=session.name or f"role_{session_id}", tasks=tasks)

        session.status = SessionStatus.COMPLETED
        self.repo.update(session)

        return role, report

    def export_artifact(self, role: Role, session_id: UUID) -> str:
        """Generate and upload role artifact."""
        import tempfile
        import zipfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            role_path = Path(tmpdir) / role.name
            role_path.mkdir()

            self.generator.generate(role, str(role_path))

            # Zip the role
            zip_path = Path(tmpdir) / f"{role.name}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file in role_path.rglob("*"):
                    if file.is_file():
                        zipf.write(file, file.relative_to(role_path.parent))

            with open(zip_path, "rb") as f:
                artifact_data = f.read()

            key = f"sessions/{session_id}/role.zip"
            return self.store.upload(key, artifact_data, "application/zip")
