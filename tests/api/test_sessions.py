"""Session endpoint tests."""

from fastapi.testclient import TestClient


def test_create_session(client: TestClient) -> None:
    """Test session creation."""
    response = client.post("/api/v1/sessions", json={"name": "test-session", "metadata": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert "id" in data


def test_create_session_with_tags(client: TestClient) -> None:
    """Test session creation with tags."""
    response = client.post(
        "/api/v1/sessions",
        json={"name": "test-session", "metadata": {}, "tags": ["production", "database"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert data["tags"] == ["production", "database"]
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


def test_list_sessions_with_tag_filter(client: TestClient) -> None:
    """Test listing sessions filtered by tags."""
    # Create sessions with different tags
    client.post(
        "/api/v1/sessions",
        json={"name": "prod-session", "tags": ["production", "database"]}
    )
    client.post(
        "/api/v1/sessions",
        json={"name": "dev-session", "tags": ["development", "database"]}
    )
    client.post(
        "/api/v1/sessions",
        json={"name": "test-session", "tags": ["production", "web"]}
    )

    # Filter by single tag
    response = client.get("/api/v1/sessions?tags=production")
    assert response.status_code == 200
    sessions = response.json()["sessions"]
    assert len(sessions) == 2
    assert all("production" in s["tags"] for s in sessions)

    # Filter by multiple tags (AND logic)
    response = client.get("/api/v1/sessions?tags=production,database")
    assert response.status_code == 200
    sessions = response.json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["name"] == "prod-session"
