"""API tests for report endpoint with enhanced statistics."""

import pytest
from fastapi.testclient import TestClient


def test_get_report_includes_enhanced_statistics(client: TestClient) -> None:
    """Test that report endpoint returns enhanced statistics."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Upload events with commands
    events = [
        {
            "timestamp": 1.0,
            "event_type": "o",
            "data": "sudo apt-get install -y nginx\n",
            "sequence": 0,
        },
        {
            "timestamp": 2.0,
            "event_type": "o",
            "data": "sudo apt-get install -y curl\n",
            "sequence": 1,
        },
        {
            "timestamp": 3.0,
            "event_type": "o",
            "data": "sudo systemctl start nginx\n",
            "sequence": 2,
        },
        {
            "timestamp": 4.0,
            "event_type": "o",
            "data": "mkdir -p /var/www\n",
            "sequence": 3,
        },
    ]

    client.post(f"/sessions/{session_id}/events", json=events)

    # Compile to generate commands
    client.post(f"/sessions/{session_id}/compile", json={})

    # Get report
    response = client.get(f"/sessions/{session_id}/report")
    assert response.status_code == 200

    data = response.json()

    # Verify basic fields
    assert data["session_id"] == session_id
    assert data["total_commands"] == 4

    # Verify enhanced statistics
    assert "module_breakdown" in data
    assert isinstance(data["module_breakdown"], dict)
    assert "apt" in data["module_breakdown"]
    assert data["module_breakdown"]["apt"] == 2

    assert "high_confidence_percentage" in data
    assert "medium_confidence_percentage" in data
    assert "low_confidence_percentage" in data
    assert isinstance(data["high_confidence_percentage"], float)

    assert "session_duration_seconds" in data
    assert isinstance(data["session_duration_seconds"], float)
    assert data["session_duration_seconds"] > 0

    assert "most_common_commands" in data
    assert isinstance(data["most_common_commands"], list)
    assert len(data["most_common_commands"]) <= 5

    assert "sudo_command_count" in data
    assert data["sudo_command_count"] == 3  # Three sudo commands


def test_get_report_handles_missing_commands(client: TestClient) -> None:
    """Test that report endpoint handles sessions without commands."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Try to get report without commands
    response = client.get(f"/sessions/{session_id}/report")

    # Should either succeed with empty report or fail gracefully
    # The endpoint will try to extract commands, so it depends on whether there are events
    assert response.status_code in [200, 400]


def test_get_report_auto_extracts_commands(client: TestClient) -> None:
    """Test that report endpoint automatically extracts commands if needed."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Upload events but don't compile
    events = [
        {
            "timestamp": 1.0,
            "event_type": "o",
            "data": "apt-get update\n",
            "sequence": 0,
        },
        {
            "timestamp": 2.0,
            "event_type": "o",
            "data": "apt-get install nginx\n",
            "sequence": 1,
        },
    ]

    client.post(f"/sessions/{session_id}/events", json=events)

    # Get report (should auto-extract commands)
    response = client.get(f"/sessions/{session_id}/report")
    assert response.status_code == 200

    data = response.json()
    assert data["total_commands"] == 2


def test_get_report_returns_404_for_nonexistent_session(client: TestClient) -> None:
    """Test that report endpoint returns 404 for nonexistent session."""
    from uuid import uuid4

    fake_id = str(uuid4())
    response = client.get(f"/sessions/{fake_id}/report")
    assert response.status_code == 404


def test_get_report_percentages_sum_to_100(client: TestClient) -> None:
    """Test that confidence percentages are calculated correctly."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Upload events with mix of command types
    events = [
        {
            "timestamp": 1.0,
            "event_type": "o",
            "data": "apt-get install nginx\n",  # High confidence
            "sequence": 0,
        },
        {
            "timestamp": 2.0,
            "event_type": "o",
            "data": "apt-get install curl\n",  # High confidence
            "sequence": 1,
        },
        {
            "timestamp": 3.0,
            "event_type": "o",
            "data": "unknown-command-xyz\n",  # Low confidence (shell fallback)
            "sequence": 2,
        },
    ]

    client.post(f"/sessions/{session_id}/events", json=events)
    client.post(f"/sessions/{session_id}/compile", json={})

    # Get report
    response = client.get(f"/sessions/{session_id}/report")
    assert response.status_code == 200

    data = response.json()

    # Percentages should sum to approximately 100 (allowing for rounding)
    total_percentage = (
        data["high_confidence_percentage"]
        + data["medium_confidence_percentage"]
        + data["low_confidence_percentage"]
    )
    assert total_percentage == pytest.approx(100.0, abs=0.01)


def test_get_report_most_common_commands_format(client: TestClient) -> None:
    """Test that most_common_commands is in the correct format."""
    # Create session
    create_resp = client.post("/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Upload events with duplicate commands
    events = [
        {
            "timestamp": 1.0,
            "event_type": "o",
            "data": "apt-get update\n",
            "sequence": 0,
        },
        {
            "timestamp": 2.0,
            "event_type": "o",
            "data": "apt-get update\n",  # Duplicate
            "sequence": 1,
        },
        {
            "timestamp": 3.0,
            "event_type": "o",
            "data": "apt-get update\n",  # Duplicate
            "sequence": 2,
        },
    ]

    client.post(f"/sessions/{session_id}/events", json=events)
    client.post(f"/sessions/{session_id}/compile", json={})

    # Get report
    response = client.get(f"/sessions/{session_id}/report")
    assert response.status_code == 200

    data = response.json()

    # Verify format
    assert "most_common_commands" in data
    assert isinstance(data["most_common_commands"], list)
    if len(data["most_common_commands"]) > 0:
        first_item = data["most_common_commands"][0]
        assert "command" in first_item
        assert "count" in first_item
        assert isinstance(first_item["command"], str)
        assert isinstance(first_item["count"], int)

