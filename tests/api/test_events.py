"""Events endpoint tests."""

from fastapi.testclient import TestClient


def test_upload_events(client: TestClient) -> None:
    """Test uploading events."""
    # Create session
    create_resp = client.post(
        "/sessions", json={"name": "test-session", "metadata": {}}
    )
    session_id = create_resp.json()["id"]

    # Upload events
    events = [
        {"timestamp": 1.0, "event_type": "o", "data": "echo hello\n", "sequence": 0}
    ]
    response = client.post(f"/sessions/{session_id}/events", json=events)
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
