"""Asciinema .cast file parser adapter."""

import json
import re
from uuid import UUID

from cli2ansible.domain.models import Event
from cli2ansible.domain.ports import CapturePort

# ANSI escape sequence pattern
ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]|\x1B\][^\x07]*\x07|\x1B[\(\)][A-Za-z]")

# OSC sequence pattern to extract window title (command)
# Format: ESC ] 2 ; command BEL
OSC_TITLE_RE = re.compile(r"\x1B\]2;([^\x07]+)\x07")


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences from string."""
    return ANSI_RE.sub("", s)


def extract_command_from_osc(s: str) -> str | None:
    """Extract command from OSC window title sequence."""
    match = OSC_TITLE_RE.search(s)
    if match:
        return match.group(1)
    return None


def apply_edit(buf: str, ch: str) -> str:
    """Apply character edit to buffer, handling backspace/delete and control sequences."""
    # backspace / delete
    if ch in ("\u0008", "\u007f"):
        return buf[:-1] if buf else buf
    # ignore escape sequences (raw ESC and CSI sequences)
    # These include arrow keys, function keys, etc.
    if ch.startswith("\x1b"):
        return buf
    # ignore other control characters except printable ones
    if ord(ch) < 32 and ch not in ("\t",):
        return buf
    return buf + ch


class AsciinemaParser(CapturePort):
    """Parse asciinema .cast files into Event objects."""

    def parse_events(
        self, recording_data: bytes, max_events: int = 100_000
    ) -> list[Event]:
        """
        Parse asciinema .cast file format into Event objects.

        This parser builds commands from input events by tracking character-by-character
        input and handling backspace/delete. Only complete commands (ending with Enter)
        are emitted as events.

        Format:
        - Line 1: JSON header with metadata (version, term, timestamp, env)
        - Lines 2+: JSON arrays [timestamp, event_type, data]
          - timestamp: float (relative time in seconds)
          - event_type: "i" (input), "o" (output), "x" (exit)
          - data: string content

        Args:
            recording_data: Raw bytes from .cast file
            max_events: Maximum number of events to parse (default: 100,000)

        Returns:
            List of Event objects containing completed commands

        Raises:
            ValueError: If file format is invalid or exceeds limits
            json.JSONDecodeError: If JSON parsing fails
        """
        try:
            lines = recording_data.decode("utf-8").strip().split("\n")
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 encoding in .cast file: {e}") from e

        if not lines or not lines[0]:
            raise ValueError("Empty .cast file")

        # Parse header (line 1)
        try:
            header = json.loads(lines[0])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON header in .cast file: {e}") from e

        # Validate header structure
        if not isinstance(header, dict):
            raise ValueError("Header must be a JSON object")

        version = header.get("version")
        if version != 2 and version != 3:
            raise ValueError(
                f"Unsupported asciinema format version: {version}. "
                "Only versions 2 and 3 are supported."
            )

        # Generate a session ID
        from uuid import uuid4

        session_id = uuid4()

        # First pass: find the minimum timestamp to use as base
        base_t = None
        for line in lines[1:]:
            if not line.strip():
                continue
            try:
                event_data = json.loads(line)
                if isinstance(event_data, list) and len(event_data) >= 1:
                    t = event_data[0]
                    if isinstance(t, int | float) and (base_t is None or t < base_t):
                        base_t = t
            except (json.JSONDecodeError, IndexError):
                continue

        if base_t is None:
            base_t = 0

        # Second pass: extract commands and their enter timestamps
        # Strategy: Find OSC title events, then look backwards for the corresponding Enter keypress
        events: list[Event] = []
        seq = 0

        # Parse all events into a list first
        all_events = []
        for line in lines[1:]:
            if not line.strip():
                continue
            try:
                event_data = json.loads(line)
                if isinstance(event_data, list) and len(event_data) >= 3:
                    all_events.append(event_data)
            except json.JSONDecodeError:
                continue

        # Find commands and their timestamps
        for i, event_data in enumerate(all_events):
            t = event_data[0]
            kind = event_data[1]
            data = event_data[2]

            if (
                not isinstance(t, int | float)
                or not isinstance(kind, str)
                or not isinstance(data, str)
            ):
                continue

            # Extract commands from OSC window title sequences in output
            if kind == "o":
                cmd = extract_command_from_osc(data)
                if cmd and cmd not in (
                    "cd",
                    "pbooth@USMBP16PBOOTH:~/personal-projects/scratch",
                    "pbooth@USMBP16PBOOTH:~/personal-projects/scratch/test_1",
                ):
                    # Look backwards to find the most recent Enter keypress
                    enter_time = t
                    for j in range(i - 1, -1, -1):
                        prev_event = all_events[j]
                        if (
                            len(prev_event) >= 3
                            and prev_event[1] == "i"
                            and prev_event[2] == "\r"
                        ):
                            enter_time = prev_event[0]
                            break

                    # Enforce event count limit
                    if seq >= max_events:
                        raise ValueError(
                            f"Event count exceeds maximum allowed limit ({max_events})"
                        )

                    events.append(
                        Event(
                            session_id=session_id,
                            timestamp=round(enter_time - base_t, 6),
                            event_type="o",
                            data=cmd,
                            sequence=seq,
                        )
                    )
                    seq += 1

        return events


def parse_cast_file(
    file_path: str,
    session_id: UUID | None = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB default
) -> list[Event]:
    """
    Convenience function to parse a .cast file from disk.

    Args:
        file_path: Path to .cast file
        session_id: Optional session ID to assign to events
        max_file_size: Maximum file size in bytes (default: 10MB)

    Returns:
        List of Event objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid or file is too large
    """
    import os

    # Check file size before reading to prevent DoS
    file_size = os.path.getsize(file_path)
    if file_size > max_file_size:
        raise ValueError(
            f"File size ({file_size} bytes) exceeds maximum allowed "
            f"size ({max_file_size} bytes)"
        )

    with open(file_path, "rb") as f:
        data = f.read()

    parser = AsciinemaParser()
    events = parser.parse_events(data)

    # Override session_id if provided
    if session_id is not None:
        for event in events:
            event.session_id = session_id

    return events
