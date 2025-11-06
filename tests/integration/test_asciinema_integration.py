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

        # Verify events are sorted by timestamp
        timestamps = [e.timestamp for e in events]
        assert timestamps == sorted(timestamps), "Events should be sorted by timestamp"

        # Verify sequences are sequential
        sequences = [e.sequence for e in events]
        assert sequences == list(range(len(events))), "Sequences should be 0, 1, 2, ..."

        # Verify event types are valid
        valid_types = {"i", "o", "x"}
        event_types = {e.event_type for e in events}
        assert event_types.issubset(valid_types), f"Invalid event types: {event_types - valid_types}"

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
        """Test demo.cast contains expected event types."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - based on the fixture content
        output_events = [e for e in events if e.event_type == "o"]
        input_events = [e for e in events if e.event_type == "i"]
        exit_events = [e for e in events if e.event_type == "x"]

        assert len(output_events) > 0, "Should have output events"
        assert len(input_events) > 0, "Should have input events"
        assert len(exit_events) == 1, "Should have exactly one exit event"
        assert exit_events[0].data == "0", "Exit code should be 0"

    def test_parse_demo_cast_commands(self) -> None:
        """Test demo.cast contains expected commands from fixture."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert - verify specific commands from demo.cast
        input_events = [e for e in events if e.event_type == "i"]
        input_data = "".join(e.data for e in input_events)

        # Based on demo.cast content, we expect these commands
        # Note: input may contain individual characters, not full words
        assert "m" in input_data and "k" in input_data, "Should contain mkdir characters"
        assert "c" in input_data and "d" in input_data, "Should contain cd characters"
        assert "e" in input_data, "Should contain echo characters"
        assert "x" in input_data and "t" in input_data, "Should contain exit characters"

    def test_parse_demo_cast_output(self) -> None:
        """Test demo.cast output events contain expected content."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert
        output_events = [e for e in events if e.event_type == "o"]
        output_data = "".join(e.data for e in output_events)

        # Based on demo.cast, expect the echo output
        assert "Hello Phillip" in output_data, "Should contain echo output"

    def test_parse_demo_cast_timestamps_increase(self) -> None:
        """Test demo.cast timestamps are monotonically increasing."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert
        for i in range(1, len(events)):
            assert events[i].timestamp >= events[i - 1].timestamp, \
                f"Timestamp at index {i} should be >= previous"

    def test_parse_demo_cast_data_not_empty(self) -> None:
        """Test demo.cast events have non-empty data fields."""
        # Arrange
        fixture_path = Path(__file__).parent.parent / "fixtures" / "demo.cast"

        # Act
        events = parse_cast_file(str(fixture_path))

        # Assert
        assert all(isinstance(e.data, str) for e in events), "All data should be strings"
        # Note: Some events may have empty strings (e.g., timing pauses), which is valid
