"""Tests for .augment/skills/docker-dev/scripts/docker.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/docker-dev/scripts"
sys.path.insert(0, str(script_path))

import docker


class TestGetComposeCmd:
    """Tests for get_compose_cmd function."""

    @patch("docker.subprocess.run")
    def test_get_compose_cmd_v2(self, mock_run):
        """Test detection of docker compose v2."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = docker.get_compose_cmd()

        assert result == ["docker", "compose"]
        mock_run.assert_called_once_with(
            ["docker", "compose", "version"], capture_output=True, check=False
        )

    @patch("docker.subprocess.run")
    def test_get_compose_cmd_v1(self, mock_run):
        """Test fallback to docker-compose v1."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = docker.get_compose_cmd()

        assert result == ["docker-compose"]


class TestRunCompose:
    """Tests for run_compose function."""

    @patch("docker.get_compose_cmd")
    @patch("docker.subprocess.run")
    def test_run_compose_success(self, mock_run, mock_get_cmd, capsys):
        """Test successful compose command."""
        mock_get_cmd.return_value = ["docker", "compose"]
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = docker.run_compose(["ps"])

        assert result is True
        mock_run.assert_called_once()
        captured = capsys.readouterr()
        assert "Success output" in captured.out

    @patch("docker.get_compose_cmd")
    @patch("docker.subprocess.run")
    def test_run_compose_failure(self, mock_run, mock_get_cmd, capsys):
        """Test failed compose command."""
        mock_get_cmd.return_value = ["docker", "compose"]
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result

        result = docker.run_compose(["invalid"])

        assert result is False
        captured = capsys.readouterr()
        assert "Error output" in captured.out

    @patch("docker.get_compose_cmd")
    @patch("docker.subprocess.run")
    def test_run_compose_follow_mode(self, mock_run, mock_get_cmd, capsys):
        """Test compose command in follow mode."""
        mock_get_cmd.return_value = ["docker", "compose"]
        mock_run.return_value = None

        result = docker.run_compose(["logs", "-f"], follow=True)

        assert result is None
        mock_run.assert_called_once()
        # In follow mode, check=False is used
        assert mock_run.call_args[1]["check"] is False


class TestCmdUp:
    """Tests for cmd_up function."""

    @patch("docker.run_compose")
    def test_cmd_up_all_services(self, mock_run_compose, capsys):
        """Test starting all services."""
        mock_run_compose.return_value = True

        docker.cmd_up([])

        mock_run_compose.assert_called_once_with(["up", "-d"])
        captured = capsys.readouterr()
        assert "Starting" in captured.out
        assert "localhost:8000" in captured.out

    @patch("docker.run_compose")
    def test_cmd_up_specific_services(self, mock_run_compose, capsys):
        """Test starting specific services."""
        mock_run_compose.return_value = True

        docker.cmd_up(["postgres", "minio"])

        mock_run_compose.assert_called_once_with(["up", "-d", "postgres", "minio"])


class TestCmdDown:
    """Tests for cmd_down function."""

    @patch("docker.run_compose")
    def test_cmd_down(self, mock_run_compose, capsys):
        """Test stopping services."""
        docker.cmd_down([])

        mock_run_compose.assert_called_once_with(["down"])
        captured = capsys.readouterr()
        assert "Stopping" in captured.out


class TestCmdRestart:
    """Tests for cmd_restart function."""

    @patch("docker.run_compose")
    def test_cmd_restart_all(self, mock_run_compose, capsys):
        """Test restarting all services."""
        docker.cmd_restart([])

        mock_run_compose.assert_called_once_with(["restart"])
        captured = capsys.readouterr()
        assert "Restarting" in captured.out

    @patch("docker.run_compose")
    def test_cmd_restart_specific(self, mock_run_compose, capsys):
        """Test restarting specific services."""
        docker.cmd_restart(["app"])

        mock_run_compose.assert_called_once_with(["restart", "app"])

