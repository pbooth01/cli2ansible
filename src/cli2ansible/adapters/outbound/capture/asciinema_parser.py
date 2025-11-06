"""Asciinema .cast file parser adapter."""

import json
from uuid import UUID

from cli2ansible.domain.models import Event
from cli2ansible.domain.ports import CapturePort


class AsciinemaParser(CapturePort):
    """Parse asciinema .cast files into Event objects."""

    def parse_events(self, recording_data: bytes, max_events: int = 100_000) -> list[Event]:
        """
        Parse asciinema .cast file format into Event objects.

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
            List of Event objects sorted by timestamp

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

        # Generate a session ID from header timestamp or use a fixed UUID
        # In real usage, this would come from the session creation
        from uuid import uuid4

        session_id = uuid4()

        # Parse event lines
        events: list[Event] = []
        for idx, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue

            # Enforce event count limit to prevent DoS
            if len(events) >= max_events:
                raise ValueError(
                    f"Event count exceeds maximum allowed limit ({max_events})"
                )

            try:
                event_data = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {idx}: {e}") from e

            # Validate event structure
            if not isinstance(event_data, list) or len(event_data) < 2:
                raise ValueError(
                    f"Line {idx}: Event must be array with at least "
                    "[timestamp, event_type]"
                )

            timestamp = event_data[0]
            event_type = event_data[1]

            # Handle exit events (2 elements) vs output/input events (3 elements)
            if event_type == "x":
                # Exit event: [timestamp, "x", exit_code]
                data = str(event_data[2]) if len(event_data) > 2 else "0"
            else:
                # Output/Input event: [timestamp, event_type, data]
                if len(event_data) < 3:
                    raise ValueError(
                        f"Line {idx}: Output/input event must have data field"
                    )
                data = event_data[2]

            # Validate types
            if not isinstance(timestamp, int | float):
                raise ValueError(f"Line {idx}: Timestamp must be a number")
            if not isinstance(event_type, str):
                raise ValueError(f"Line {idx}: Event type must be a string")
            if not isinstance(data, str):
                raise ValueError(f"Line {idx}: Data must be a string")

            if event_type not in ("i", "o", "x"):
                raise ValueError(
                    f"Line {idx}: Invalid event type '{event_type}'. "
                    "Must be 'i', 'o', or 'x'"
                )

            events.append(
                Event(
                    session_id=session_id,
                    timestamp=float(timestamp),
                    event_type=event_type,
                    data=data,
                    sequence=len(events),
                )
            )

        # Sort by timestamp and reassign sequence numbers
        events.sort(key=lambda e: e.timestamp)
        for idx, event in enumerate(events):
            event.sequence = idx

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
