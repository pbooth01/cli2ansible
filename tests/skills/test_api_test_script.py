"""Tests for .augment/skills/api-test/scripts/api_test.py"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/api-test/scripts"
sys.path.insert(0, str(script_path))

import api_test


class TestCheckHealth:
    """Tests for check_health function."""

    @patch("api_test.httpx.get")
    def test_check_health_success(self, mock_get, capsys):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response

        result = api_test.check_health("http://localhost:8000")

        assert result is True
        mock_get.assert_called_once_with("http://localhost:8000/api/v1/health", timeout=5)
        captured = capsys.readouterr()
        assert "200" in captured.out
        assert "healthy" in captured.out

    @patch("api_test.httpx.get")
    def test_check_health_connection_error(self, mock_get, capsys):
        """Test health check with connection error."""
        import httpx

        mock_get.side_effect = httpx.ConnectError("Connection refused")

        result = api_test.check_health("http://localhost:8000")

        assert result is False
        captured = capsys.readouterr()
        assert "Cannot connect" in captured.out


class TestCreateSession:
    """Tests for create_session function."""

    @patch("api_test.httpx.post")
    def test_create_session_success(self, mock_post, capsys):
        """Test successful session creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "test-session-id"}
        mock_post.return_value = mock_response

        result = api_test.create_session("http://localhost:8000", "Test Session")

        assert result == "test-session-id"
        mock_post.assert_called_once()
        captured = capsys.readouterr()
        assert "test-session-id" in captured.out

    @patch("api_test.httpx.post")
    def test_create_session_failure(self, mock_post, capsys):
        """Test failed session creation."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        result = api_test.create_session("http://localhost:8000", "Test Session")

        assert result is None
        captured = capsys.readouterr()
        assert "Failed" in captured.out


class TestIngestCast:
    """Tests for ingest_cast function."""

    @patch("api_test.httpx.post")
    @patch("builtins.open", create=True)
    @patch("api_test.Path")
    def test_ingest_cast_success(self, mock_path, mock_open, mock_post, capsys):
        """Test successful cast file ingestion."""
        # Mock file existence
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.name = "test.cast"
        mock_path.return_value = mock_path_instance

        # Mock file content
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"event_count": 42}
        mock_post.return_value = mock_response

        result = api_test.ingest_cast("http://localhost:8000", "session-id", "test.cast")

        assert result is True
        captured = capsys.readouterr()
        assert "42" in captured.out

    @patch("api_test.Path")
    def test_ingest_cast_file_not_found(self, mock_path, capsys):
        """Test ingestion with non-existent file."""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        result = api_test.ingest_cast("http://localhost:8000", "session-id", "missing.cast")

        assert result is False
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestCompileSession:
    """Tests for compile_session function."""

    @patch("api_test.httpx.post")
    def test_compile_session_success(self, mock_post, capsys):
        """Test successful session compilation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "artifact_url": "http://example.com/artifact",
            "download_url": "http://example.com/download",
        }
        mock_post.return_value = mock_response

        result = api_test.compile_session("http://localhost:8000", "session-id")

        assert result is True
        captured = capsys.readouterr()
        assert "successful" in captured.out
        assert "artifact" in captured.out

    @patch("api_test.httpx.post")
    def test_compile_session_failure(self, mock_post, capsys):
        """Test failed session compilation."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        result = api_test.compile_session("http://localhost:8000", "session-id")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed" in captured.out

