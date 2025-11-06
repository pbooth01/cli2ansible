"""Unit tests for AsciinemaParser class."""

from uuid import UUID

import pytest
from cli2ansible.adapters.outbound.capture.asciinema_parser import AsciinemaParser
from cli2ansible.domain.models import Event


class TestAsciinemaParser:
    """Test suite for AsciinemaParser."""

    def test_parse_valid_v3_format(self) -> None:
        """Test parsing a valid version 3 .cast file."""
        # Arrange
        cast_data = (
            '{"version":3,"term":{"cols":80,"rows":24},"timestamp":1234567890}\n'
            '[0.0,"o","hello\\r\\n"]\n'
            '[1.5,"i","test"]\n'
            '[2.0,"x","0"]\n'
        )
        parser = AsciinemaParser()

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 3
        assert all(isinstance(e, Event) for e in events)
        assert events[0].event_type == "o"
        # JSON correctly parses the escape sequence: "hello\\r\\n" becomes "hello\r\n"
        assert events[0].data == "hello\r\n"
        assert events[0].timestamp == 0.0
        assert events[0].sequence == 0
        assert events[1].event_type == "i"
        assert events[1].data == "test"
        assert events[1].timestamp == 1.5
        assert events[1].sequence == 1
        assert events[2].event_type == "x"
        assert events[2].data == "0"
        assert events[2].timestamp == 2.0
        assert events[2].sequence == 2

    def test_parse_valid_v2_format(self) -> None:
        """Test parsing a valid version 2 .cast file."""
        # Arrange
        cast_data = (
            '{"version":2,"width":80,"height":24}\n'
            '[0.5,"o","output text"]\n'
            '[1.0,"i","input text"]\n'
        )
        parser = AsciinemaParser()

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 2
        assert events[0].event_type == "o"
        assert events[0].timestamp == 0.5
        assert events[1].event_type == "i"
        assert events[1].timestamp == 1.0

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

    def test_parse_invalid_event_json(self) -> None:
        """Test parsing file with malformed event JSON raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o","test"]\n[1.0,invalid json'

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON on line 3"):
            parser.parse_events(cast_data)

    def test_parse_event_not_array(self) -> None:
        """Test parsing event that's not an array raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n{"timestamp":0.0,"type":"o"}'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Event must be array"):
            parser.parse_events(cast_data)

    def test_parse_event_missing_data(self) -> None:
        """Test parsing output event without data field raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Output/input event must have data field"):
            parser.parse_events(cast_data)

    def test_parse_invalid_timestamp_type(self) -> None:
        """Test parsing event with non-numeric timestamp raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n["0.0","o","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Timestamp must be a number"):
            parser.parse_events(cast_data)

    def test_parse_invalid_event_type(self) -> None:
        """Test parsing event with unknown type raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"z","test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Invalid event type 'z'"):
            parser.parse_events(cast_data)

    def test_parse_exit_event(self) -> None:
        """Test parsing exit event with 2 elements correctly."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"x","0"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "x"
        assert events[0].data == "0"

    def test_parse_exit_event_no_code(self) -> None:
        """Test parsing exit event without exit code defaults to "0"."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"x"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "x"
        assert events[0].data == "0"

    def test_parse_sorts_by_timestamp(self) -> None:
        """Test parsing events out of order returns sorted by timestamp."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = (
            '{"version":3}\n'
            '[2.0,"o","third"]\n'
            '[0.5,"o","first"]\n'
            '[1.0,"o","second"]\n'
        )

        # Act
        events = parser.parse_events(cast_data.encode("utf-8"))

        # Assert
        assert len(events) == 3
        assert events[0].timestamp == 0.5
        assert events[0].data == "first"
        assert events[0].sequence == 0
        assert events[1].timestamp == 1.0
        assert events[1].data == "second"
        assert events[1].sequence == 1
        assert events[2].timestamp == 2.0
        assert events[2].data == "third"
        assert events[2].sequence == 2

    def test_parse_empty_lines(self) -> None:
        """Test parsing file with blank lines skips them."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o","test"]\n\n[1.0,"o","test2"]\n\n'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 2
        assert events[0].data == "test"
        assert events[1].data == "test2"

    def test_parse_output_events(self) -> None:
        """Test parsing "o" type events creates output events."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o","stdout text"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "o"
        assert events[0].data == "stdout text"

    def test_parse_input_events(self) -> None:
        """Test parsing "i" type events creates input events."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"i","user input"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].event_type == "i"
        assert events[0].data == "user input"

    def test_parse_integer_timestamp(self) -> None:
        """Test parsing events with integer timestamps."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[1,"o","test"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 1
        assert events[0].timestamp == 1.0
        assert isinstance(events[0].timestamp, float)

    def test_parse_generates_session_id(self) -> None:
        """Test parsing generates a session_id for events."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o","test1"]\n[1.0,"o","test2"]'

        # Act
        events = parser.parse_events(cast_data)

        # Assert
        assert len(events) == 2
        assert isinstance(events[0].session_id, UUID)
        assert events[0].session_id == events[1].session_id

    def test_parse_invalid_data_type(self) -> None:
        """Test parsing event with non-string data raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,"o",123]'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Data must be a string"):
            parser.parse_events(cast_data)

    def test_parse_invalid_event_type_field(self) -> None:
        """Test parsing event with non-string event type raises ValueError."""
        # Arrange
        parser = AsciinemaParser()
        cast_data = b'{"version":3}\n[0.0,123,"test"]'

        # Act & Assert
        with pytest.raises(ValueError, match="Line 2: Event type must be a string"):
            parser.parse_events(cast_data)
