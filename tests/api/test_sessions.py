"""Session endpoint tests."""

from fastapi.testclient import TestClient


def test_create_session(client: TestClient) -> None:
    """Test session creation."""
    response = client.post("/api/v1/sessions", json={"name": "test-session", "metadata": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert "id" in data


def test_get_session(client: TestClient) -> None:
    """Test getting a session."""
    # Create session
    create_resp = client.post("/api/v1/sessions", json={"name": "test-session", "metadata": {}})
    session_id = create_resp.json()["id"]

    # Get session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id
