"""Application service for extracting commands from terminal session events."""

import re
from uuid import UUID

from cli2ansible.domain.entities import Command
from cli2ansible.domain.ports import SessionRepositoryPort


class CommandExtractionService:
    """Service for extracting commands from terminal session events.

    This service is responsible for parsing terminal output events and
    extracting executable commands from them. It handles ANSI escape codes,
    sudo detection, and command normalization.
    """

    def __init__(self, repo: SessionRepositoryPort) -> None:
        """Initialize command extraction service with repository port.

        Args:
            repo: Repository for accessing session events and storing commands
        """
        self.repo = repo

    def extract_commands(self, session_id: UUID) -> list[Command]:
        """Extract commands from session events.

        Parses terminal output events to identify and extract commands,
        handling multi-line output, ANSI codes, and sudo detection.

        Args:
            session_id: UUID of the session to extract commands from

        Returns:
            List of extracted Command entities
        """
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
                            line, session_id, event.timestamp, event.sequence
                        )
                        if cmd:
                            commands.append(cmd)
                    current_line = lines[-1]
                else:
                    # If there's no newline, treat each event as a potential command
                    cmd = self._parse_command_line(
                        current_line, session_id, event.timestamp, event.sequence
                    )
                    if cmd:
                        commands.append(cmd)
                    current_line = ""

        # Process any remaining line
        if current_line and events:
            cmd = self._parse_command_line(
                current_line, session_id, events[-1].timestamp, events[-1].sequence
            )
            if cmd:
                commands.append(cmd)

        self.repo.save_commands(commands)
        return commands

    def _parse_command_line(
        self, line: str, session_id: UUID, timestamp: float, event_sequence: int = 0
    ) -> Command | None:
        """Parse a line to extract command.

        Removes ANSI escape codes, detects sudo usage, and creates
        a Command entity if the line contains a valid command.

        Args:
            line: Raw line from terminal output
            session_id: UUID of the session
            timestamp: Timestamp of the event
            event_sequence: Sequence number of the event

        Returns:
            Command entity if valid command found, None otherwise
        """
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
            event_sequence=event_sequence,
        )
