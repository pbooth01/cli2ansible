"""Unit tests for AsciinemaParser class."""

from uuid import UUID

import pytest
from cli2ansible.adapters.outbound.capture.asciinema_parser import AsciinemaParser
from cli2ansible.domain.models import Event


class TestAsciinemaParser:
    """Test suite for AsciinemaParser."""

    def test_parse_valid_v3_format(self) -> None:
        """Test parsing a valid version 3 .cast file with OSC commands."""
        # Arrange
        cast_data = (
            '{"version":3,"term":{"cols":80,"rows":24},"timestamp":1234567890}\n'
            '[0.5,"i","\\r"]\n'
            '[1.0,"o","\\u001b]2;mkdir test_dir\\u0007"]\n'
            '[1.5,"i","\\r"]\n'
            '[2.0,"o","\\u001b]2;ls -la\\u0007"]\n'
        )
        parser = AsciinemaParser()

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 2
        assert all(isinstance(e, Event) for e in events)
        assert events[0].event_type == "o"
        assert events[0].data == "mkdir test_dir"
        assert events[0].timestamp == 0.0  # Normalized: 0.5 - 0.5 (base)
        assert events[0].sequence == 0
        assert events[1].event_type == "o"
        assert events[1].data == "ls -la"
        assert events[1].timestamp == 1.0  # Normalized: 1.5 - 0.5 (base)
        assert events[1].sequence == 1

    def test_parse_valid_v2_format(self) -> None:
        """Test parsing a valid version 2 .cast file with OSC commands."""
        # Arrange
        cast_data = (
            '{"version":2,"width":80,"height":24}\n'
            '[0.5,"i","\\r"]\n'
            '[1.0,"o","\\u001b]2;echo hello\\u0007"]\n'
        )
        parser = AsciinemaParser()

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "o"
        assert events[0].data == "echo hello"
        assert events[0].timestamp == 0.0  # Normalized: 0.5 - 0.5 (base)

    def test_parse_empty_file(self) -> None:
        """Test parsing an empty file raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        empty_data = b""

        # Act & Assert
        with pytest.raises(ValueError, match="Empty .cast file"):
            parser.parse_events(empty_data)

    def test_parse_invalid_utf8(self) -> None:
        """Test parsing non-UTF8 bytes raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        invalid_data = b"\xff\xfe\xfd"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid UTF-8 encoding"):
            parser.parse_events(invalid_data)

    def test_parse_invalid_json_header(self) -> None:
        """Test parsing file with malformed JSON header raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3,invalid\n[0.0,"o","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON header"):
            parser.parse_events(cast_data)

    def test_parse_unsupported_version(self) -> None:
        """Test parsing file with unsupported version raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":1}\n[0.0,"o","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported asciinema format version: 1"):
            parser.parse_events(cast_data)

    def test_parse_header_not_dict(self) -> None:
        """Test parsing file with non-dict header raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'["version",3]\n[0.0,"o","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Header must be a JSON object"):
            parser.parse_events(cast_data)

    def test_parse_missing_version(self) -> None:
        """Test parsing file with missing version field raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"width":80,"height":24}\n[0.0,"o","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported asciinema format version: None"):
            parser.parse_events(cast_data)

    def test_parse_no_commands(self) -> None:
        """Test parsing file without OSC commands returns empty list."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o","regular output"]\n[1.0,"i","input"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 0

    def test_parse_filters_prompt_sequences(self) -> None:
        """Test that specific prompt OSC sequences are filtered out."""
        # Arrange
        parser = AsciinemaParser()
        # Note: Parser has hardcoded filters for specific prompts
        # This test uses "cd" which is filtered
        cast_data = (
            '{"version":3}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;cd\\u0007"]\n'
            '[1.0,"i","\\r"]\n'
            '[1.5,"o","\\u001b]2;mkdir test\\u0007"]\n'
        )

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 1
        assert events[0].data == "mkdir test"

    def test_parse_maintains_order(self) -> None:
        """Test parsing events maintains order from file (no sorting)."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            '{"version":3}\n'
            '[2.0,"i","\\r"]\n'
            '[2.5,"o","\\u001b]2;ls\\u0007"]\n'
            '[0.5,"i","\\r"]\n'
            '[1.0,"o","\\u001b]2;pwd\\u0007"]\n'
        )

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert - parser doesn't sort, maintains file order
        assert len(events) == 2
        assert events[0].data == "ls"  # First in file
        assert events[0].timestamp == 1.5  # 2.0 - 0.5 (base is 0.5)
        assert events[1].data == "pwd"  # Second in file
        assert events[1].timestamp == 0.0  # 0.5 - 0.5 (base)

    def test_parse_empty_lines(self) -> None:
        """Test parsing file with blank lines skips them."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[0.0,"i","\\r"]\n'
            b'\n'
            b'[1.0,"o","\\u001b]2;echo test\\u0007"]\n'
            b'\n'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].data == "echo test"

    def test_parse_output_events(self) -> None:
        """Test parsing OSC commands from output events."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[0.0,"i","\\r"]\n'
            b'[0.5,"o","\\u001b]2;git status\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "o"
        assert events[0].data == "git status"

    def test_parse_input_events(self) -> None:
        """Test that input events are used for Enter timestamp."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[0.0,"i","m"]\n'
            b'[0.1,"i","k"]\n'
            b'[0.2,"i","d"]\n'
            b'[0.3,"i","i"]\n'
            b'[0.4,"i","r"]\n'
            b'[0.5,"i","\\r"]\n'
            b'[1.0,"o","\\u001b]2;mkdir\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].timestamp == 0.5  # 0.5 (Enter) - 0.0 (base)

    def test_parse_integer_timestamp(self) -> None:
        """Test parsing events with integer timestamps."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[1,"i","\\r"]\n'
            b'[2,"o","\\u001b]2;ls\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].timestamp == 0  # 1 - 1 (base)
        assert isinstance(events[0].timestamp, int | float)

    def test_parse_generates_session_id(self) -> None:
        """Test parsing generates a session_id for events."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[0.0,"i","\\r"]\n'
            b'[1.0,"o","\\u001b]2;pwd\\u0007"]\n'
            b'[2.0,"i","\\r"]\n'
            b'[3.0,"o","\\u001b]2;ls\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 2
        assert isinstance(events[0].session_id, UUID)
        assert events[0].session_id == events[1].session_id

    def test_parse_max_events_limit(self) -> None:
        """Test that parser enforces max_events limit."""
        # Arrange
        parser = AsciinemaParser()
        # Create cast data with 3 commands
        cast_data = (
            b'{"version":3}\n'
            b'[0.0,"i","\\r"]\n'
            b'[1.0,"o","\\u001b]2;cmd1\\u0007"]\n'
            b'[2.0,"i","\\r"]\n'
            b'[3.0,"o","\\u001b]2;cmd2\\u0007"]\n'
            b'[4.0,"i","\\r"]\n'
            b'[5.0,"o","\\u001b]2;cmd3\\u0007"]'
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Event count exceeds maximum allowed limit"):
            parser.parse_events(cast_data, max_events=2)

    def test_parse_extracts_command_without_enter(self) -> None:
        """Test that commands without Enter use OSC timestamp."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[1.0,"o","\\u001b]2;ls\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].data == "ls"
        assert events[0].timestamp == 0.0  # 1.0 - 1.0 (base, normalized)

    def test_parse_normalizes_timestamp_to_base(self) -> None:
        """Test that timestamps are normalized relative to first event."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            b'{"version":3}\n'
            b'[10.0,"i","\\r"]\n'
            b'[11.0,"o","\\u001b]2;pwd\\u0007"]\n'
            b'[20.0,"i","\\r"]\n'
            b'[21.0,"o","\\u001b]2;ls\\u0007"]'
        )

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 2
        assert events[0].timestamp == 0.0  # 10.0 - 10.0
        assert events[1].timestamp == 10.0  # 20.0 - 10.0
