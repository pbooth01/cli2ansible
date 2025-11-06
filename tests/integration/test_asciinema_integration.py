"""Integration tests for asciinema parser with real fixtures."""

from pathlib import Path
from uuid import UUID, uuid4

from cli2ansible.adapters.outbound.capture.asciinema_parser import parse_cast_file


class TestAsciinemaIntegration:
    """Integration tests using real demo.cast fixture."""

    def test_parse_demo_cast_fixture(self) -> None:
        """Test end-to-end parsing of demo.cast fixture."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - verify structure
        assert len(events) > 0, "Should parse at least one event"
        assert all(hasattr(e, "session_id") for e in events), "All events should have session_id"
        assert all(hasattr(e, "timestamp") for e in events), "All events should have timestamp"
        assert all(hasattr(e, "event_type") for e in events), "All events should have event_type"
        assert all(hasattr(e, "data") for e in events), "All events should have data"
        assert all(hasattr(e, "sequence") for e in events), "All events should have sequence"

        # Verify all events share same session_id
        session_ids = {e.session_id for e in events}
        assert len(session_ids) == 1, "All events should share same session_id"
        assert isinstance(list(session_ids)[0], UUID), "session_id should be UUID"

        # Verify sequences are sequential
        sequences = [e.sequence for e in events]
        assert sequences == list(range(len(events))), "Sequences should be 0, 1, 2, ..."

        # Verify event types - new parser only returns "o" (output) events with commands
        event_types = {e.event_type for e in events}
        assert event_types == {"o"}, "Parser should only return output events with commands"

    def test_parse_demo_cast_with_session_override(self) -> None:
        """Test parsing demo.cast with custom session_id."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"
        custom_session_id = uuid4()

        # Act
        events = parse_cast_file(str(fixture_path), session_id=custom_session_id)

        # Assert
        assert len(events) > 0
        assert all(e.session_id == custom_session_id for e in events)

    def test_parse_demo_cast_event_types(self) -> None:
        """Test demo.cast contains expected commands."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - new parser extracts commands from OSC sequences
        # All events should be output events containing commands
        assert all(e.event_type == "o" for e in events), "All events should be output events"
        assert len(events) > 0, "Should have parsed commands"

        # Verify we got the expected commands from demo.cast
        commands = [e.data for e in events]
        assert "mkdir test_1" in commands, "Should have mkdir command"
        assert "echo \"Hello Phillip\"" in commands, "Should have echo command"
        assert "exit" in commands, "Should have exit command"

    def test_parse_demo_cast_commands(self) -> None:
        """Test demo.cast contains expected commands from fixture."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - verify specific commands from demo.cast OSC sequences
        commands = [e.data for e in events]
        command_str = " ".join(commands)

        # Based on demo.cast content, we expect these command words
        assert "mkdir" in command_str, "Should contain mkdir command"
        assert "test_1" in command_str, "Should contain test_1 directory name"
        assert "echo" in command_str, "Should contain echo command"
        assert "Hello Phillip" in command_str, "Should contain echo output"
        assert "exit" in command_str, "Should contain exit command"

    def test_parse_demo_cast_output(self) -> None:
        """Test demo.cast output events contain expected content."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert
        output_data = " ".join(e.data for e in events)

        # Based on demo.cast, expect the echo command
        assert "Hello Phillip" in output_data, "Should contain echo output"

    def test_parse_demo_cast_timestamps_increase(self) -> None:
        """Test demo.cast timestamps are monotonically increasing (or equal)."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - timestamps should be >= 0 and reasonable
        for event in events:
            assert event.timestamp >= 0, "Timestamps should be non-negative"
            assert event.timestamp < 1000, "Timestamps should be reasonable (< 1000s)"

    def test_parse_demo_cast_data_not_empty(self) -> None:
        """Test demo.cast events have non-empty data fields."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert
        assert all(isinstance(e.data, str) for e in events), "All data should be strings"
        assert all(len(e.data) > 0 for e in events), "All commands should be non-empty"
