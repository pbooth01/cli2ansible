"""Domain services (business logic)."""

import re
from typing import Any
from uuid import UUID, uuid4

from cli2ansible.domain.models import (
    CleanedCommand,
    CleaningReport,
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
    CapturePort,
    LLMPort,
    ObjectStorePort,
    RoleGeneratorPort,
    SessionRepositoryPort,
    TranslatorPort,
)


class VersionConflictError(Exception):
    """Raised when an event update has a version conflict."""

    pass


class IngestSession:
    """Service for ingesting terminal sessions."""

    def __init__(
        self,
        repo: SessionRepositoryPort,
        parser: CapturePort | None = None,
        store: ObjectStorePort | None = None,
    ) -> None:
        self.repo = repo
        self.parser = parser
        self.store = store

    def create_session(
        self, name: str, metadata: dict[str, Any] | None = None
    ) -> Session:
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
                # Process lines if we have newlines OR if this is a new event without continuation
                if "\n" in current_line or "\r" in current_line:
                    lines = current_line.split("\n")
                    for line in lines[:-1]:
                        cmd = self._parse_command_line(
                            line, session_id, event.timestamp
                        )
                        if cmd:
                            commands.append(cmd)
                    current_line = lines[-1]
                else:
                    # If there's no newline, treat each event as a potential command
                    cmd = self._parse_command_line(
                        current_line, session_id, event.timestamp
                    )
                    if cmd:
                        commands.append(cmd)
                    current_line = ""

        # Process any remaining line
        if current_line:
            cmd = self._parse_command_line(
                current_line, session_id, events[-1].timestamp if events else 0.0
            )
            if cmd:
                commands.append(cmd)

        self.repo.save_commands(commands)
        return commands

    def _parse_command_line(
        self, line: str, session_id: UUID, timestamp: float
    ) -> Command | None:
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

    def upload_cast_file(
        self, session_id: UUID, file_data: bytes, filename: str
    ) -> list[Event]:
        """
        Upload .cast file, store in MinIO, parse, and save events.

        Returns parsed events with IDs and versions.

        Raises:
            ValueError: If session not found or file invalid
        """
        if not self.parser:
            raise ValueError("Parser not configured")
        if not self.store:
            raise ValueError("Object store not configured")

        # 1. Validate session exists
        session = self.repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 2. Validate file size
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            raise ValueError("File size exceeds maximum (10MB)")

        # 3. Parse file to validate format
        try:
            events = self.parser.parse_events(file_data)
        except Exception as e:
            raise ValueError(f"Invalid .cast file format: {e}") from e

        # 4. Store file in MinIO
        key = f"sessions/{session_id}/recording.cast"
        self.store.upload(key, file_data, "application/json")

        # 5. Assign event IDs and versions
        for event in events:
            event.id = uuid4()
            event.session_id = session_id
            event.version = 1

        # 6. Save events to database
        self.repo.save_events(events)

        # 7. Update session metadata and status
        session.metadata["cast_file_key"] = key
        session.metadata["cast_filename"] = filename
        session.status = SessionStatus.UPLOADED
        self.repo.update(session)

        return events

    def update_events_batch(
        self, session_id: UUID, updates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Update multiple events in a batch with partial success support.

        Returns list of results with status for each update.
        Each result: {"id": UUID, "status": "success"|"error", "event": Event | None, "error": str | None}

        Note: Uses individual transactions per event to enable partial success.
        """
        results = []

        for update_spec in updates:
            event_id = UUID(update_spec["id"])
            expected_version = update_spec["version"]

            try:
                event = self.repo.get_event_by_id(event_id)
                if not event:
                    results.append(
                        {
                            "id": str(event_id),
                            "status": "error",
                            "error": f"Event {event_id} not found",
                        }
                    )
                    continue

                if event.session_id != session_id:
                    results.append(
                        {
                            "id": str(event_id),
                            "status": "error",
                            "error": "Event does not belong to this session",
                        }
                    )
                    continue

                if event.version != expected_version:
                    results.append(
                        {
                            "id": str(event_id),
                            "status": "error",
                            "error": f"Version conflict: expected {expected_version}, current is {event.version}",
                        }
                    )
                    continue

                # Apply updates
                for key, value in update_spec.items():
                    if key in ("timestamp", "data", "event_type"):
                        setattr(event, key, value)

                # Increment version
                event.version += 1

                # Save
                updated_event = self.repo.update_event(event)

                results.append(
                    {
                        "id": str(event_id),
                        "status": "success",
                        "event": updated_event,  # type: ignore[dict-item]
                    }
                )

            except Exception as e:
                results.append(
                    {"id": str(event_id), "status": "error", "error": str(e)}
                )

        return results

    def update_event(
        self,
        session_id: UUID,
        event_id: UUID,
        updates: dict[str, Any],
        expected_version: int,
    ) -> Event:
        """
        Update a single event with optimistic locking (convenience method).

        Raises:
            ValueError: If event not found
            VersionConflictError: If version mismatch
        """
        event = self.repo.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        if event.session_id != session_id:
            raise ValueError("Event does not belong to this session")

        if event.version != expected_version:
            raise VersionConflictError(
                f"Version conflict: expected {expected_version}, "
                f"current is {event.version}"
            )

        # Apply updates
        for key, value in updates.items():
            if key in ("timestamp", "data", "event_type"):
                setattr(event, key, value)

        # Increment version
        event.version += 1

        # Save
        return self.repo.update_event(event)


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
        from collections import Counter

        session = self.repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = SessionStatus.COMPILING
        self.repo.update(session)

        commands = self.repo.get_commands(session_id)
        tasks: list[Task] = []
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
            report.high_confidence_percentage = (report.high_confidence / report.total_commands) * 100
            report.medium_confidence_percentage = (report.medium_confidence / report.total_commands) * 100
            report.low_confidence_percentage = (report.low_confidence / report.total_commands) * 100

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
            result: str = self.store.upload(key, artifact_data, "application/zip")
            return result


class CleanSession:
    """Service for cleaning terminal session output."""

    def __init__(self, repo: SessionRepositoryPort, llm: LLMPort) -> None:
        self.repo = repo
        self.llm = llm

    def clean_commands(
        self, session_id: UUID
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """
        Clean terminal session by removing duplicates and error corrections.

        Uses LLM to intelligently identify:
        - Duplicate commands that were run multiple times
        - Error corrections where user fixed typos or mistakes
        - Redundant commands that don't add value
        """
        commands = self.repo.get_commands(session_id)
        if not commands:
            return [], CleaningReport(
                session_id=session_id,
                original_command_count=0,
                cleaned_command_count=0,
                duplicates_removed=0,
                error_corrections_removed=0,
                cleaning_rationale="No commands found in session",
            )

        cleaned_commands, report = self.llm.clean_commands(commands, session_id)
        return cleaned_commands, report

    def get_essential_commands(self, session_id: UUID) -> list[str]:
        """Get the essential commands needed to reproduce the session."""
        cleaned_commands, _ = self.clean_commands(session_id)
        return [cmd.command for cmd in cleaned_commands if not cmd.is_duplicate]
