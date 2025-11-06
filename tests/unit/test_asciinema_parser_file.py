"""Unit tests for parse_cast_file helper function."""

import tempfile
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from cli2ansible.adapters.outbound.capture.asciinema_parser import parse_cast_file


class TestParseCastFile:
    """Test suite for parse_cast_file function."""

    def test_parse_cast_file_success(self) -> None:
        """Test reading and parsing a .cast file from disk."""
        # Arrange - use OSC sequences for commands
        cast_content = (
            '{"version":3,"term":{"cols":80,"rows":24},"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;mkdir test\\u0007"]\n'
            '[1.0,"i","\\r"]\n'
            '[1.5,"o","\\u001b]2;ls\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            events = parse_cast_file(temp_path)

            # Assert
            assert len(events) == 2
            assert events[0].event_type == "o"
            assert events[0].data == "mkdir test"
            assert events[1].event_type == "o"
            assert events[1].data == "ls"
            assert isinstance(events[0].session_id, UUID)
        finally:
            Path(temp_path).unlink()

    def test_parse_cast_file_not_found(self) -> None:
        """Test reading non-existent file raises FileNotFoundError."""
        # Arrange
        nonexistent_path = "/tmp/nonexistent_file_12345.cast"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            parse_cast_file(nonexistent_path)

    def test_parse_cast_file_session_override(self) -> None:
        """Test overriding session_id assigns new ID to all events."""
        # Arrange - use OSC sequences
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;pwd\\u0007"]\n'
            '[1.0,"i","\\r"]\n'
            '[1.5,"o","\\u001b]2;ls\\u0007"]\n'
        )
        custom_session_id = uuid4()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            events = parse_cast_file(temp_path, session_id=custom_session_id)

            # Assert
            assert len(events) == 2
            assert all(e.session_id == custom_session_id for e in events)
        finally:
            Path(temp_path).unlink()

    def test_parse_cast_file_invalid_format(self) -> None:
        """Test parsing invalid .cast format raises ValueError."""
        # Arrange
        invalid_content = "not a valid cast file"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name

        try:
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid JSON header"):
                parse_cast_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_parse_cast_file_empty(self) -> None:
        """Test parsing empty file raises ValueError."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            temp_path = f.name

        try:
            # Act & Assert
            with pytest.raises(ValueError, match="Empty .cast file"):
                parse_cast_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_parse_cast_file_binary_mode(self) -> None:
        """Test that file is read in binary mode."""
        # Arrange - use OSC sequence with Unicode characters
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;echo hello 世界\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cast", delete=False, encoding="utf-8"
        ) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            events = parse_cast_file(temp_path)

            # Assert
            assert len(events) == 1
            assert events[0].data == "echo hello 世界"
        finally:
            Path(temp_path).unlink()
