"""Tests for .augment/skills/git-refresh/scripts/refresh.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/git-refresh/scripts"
sys.path.insert(0, str(script_path))

import refresh


class TestRunCommand:
    """Tests for run_command function."""

    @patch("refresh.subprocess.run")
    def test_run_command_success_string(self, mock_run, capsys):
        """Test successful command execution with string command."""
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = refresh.run_command("echo test", "Test command")

        assert result is True
        mock_run.assert_called_once()
        assert mock_run.call_args[1]["shell"] is True
        captured = capsys.readouterr()
        assert "Test command" in captured.out

    @patch("refresh.subprocess.run")
    def test_run_command_success_list(self, mock_run, capsys):
        """Test successful command execution with list command."""
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = refresh.run_command(["echo", "test"], "Test command")

        assert result is True
        mock_run.assert_called_once()
        assert "shell" not in mock_run.call_args[1] or mock_run.call_args[1]["shell"] is False

    @patch("refresh.subprocess.run")
    def test_run_command_failure(self, mock_run, capsys):
        """Test failed command execution."""
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="Error message"
        )

        result = refresh.run_command("git invalid", "Invalid command")

        assert result is False
        captured = capsys.readouterr()
        assert "Error" in captured.out


class TestRefreshWorkspace:
    """Tests for refresh_workspace function."""

    @patch("refresh.subprocess.run")
    @patch("refresh.run_command")
    def test_refresh_workspace_success_no_submodules(
        self, mock_run_command, mock_subprocess_run, capsys
    ):
        """Test successful workspace refresh without submodules."""
        # Mock run_command to always succeed
        mock_run_command.return_value = True

        # Mock submodule check to return no submodules
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_subprocess_run.return_value = mock_result

        result = refresh.refresh_workspace(branch="main", remote="origin")

        assert result is True
        # Should call run_command 4 times for main repo commands
        assert mock_run_command.call_count == 4
        captured = capsys.readouterr()
        assert "Refreshing workspace" in captured.out
        assert "complete" in captured.out

    @patch("refresh.subprocess.run")
    @patch("refresh.run_command")
    def test_refresh_workspace_success_with_submodules(
        self, mock_run_command, mock_subprocess_run, capsys
    ):
        """Test successful workspace refresh with submodules."""
        # Mock run_command to always succeed
        mock_run_command.return_value = True

        # Mock submodule check to return submodules exist
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "submodule.path value"
        mock_subprocess_run.return_value = mock_result

        result = refresh.refresh_workspace(branch="develop", remote="upstream")

        assert result is True
        # Should call run_command 4 times for main repo + 5 times for submodules
        assert mock_run_command.call_count == 9
        captured = capsys.readouterr()
        assert "Refreshing submodules" in captured.out

    @patch("refresh.run_command")
    def test_refresh_workspace_failure(self, mock_run_command, capsys):
        """Test workspace refresh failure."""
        # Mock run_command to fail on first call
        mock_run_command.return_value = False

        result = refresh.refresh_workspace()

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to refresh" in captured.out

    @patch("refresh.subprocess.run")
    @patch("refresh.run_command")
    def test_refresh_workspace_submodule_failure(
        self, mock_run_command, mock_subprocess_run, capsys
    ):
        """Test workspace refresh with submodule failure (should continue)."""
        # Mock run_command to succeed for main repo, fail for submodules
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            # First 4 calls succeed (main repo), then fail (submodules)
            return call_count[0] <= 4

        mock_run_command.side_effect = side_effect

        # Mock submodule check to return submodules exist
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "submodule.path value"
        mock_subprocess_run.return_value = mock_result

        result = refresh.refresh_workspace()

        # Should still succeed even if submodules fail
        assert result is True
        captured = capsys.readouterr()
        assert "Warning" in captured.out


class TestMain:
    """Tests for main function."""

    @patch("refresh.refresh_workspace")
    @patch("refresh.subprocess.run")
    @patch("sys.argv", ["refresh.py"])
    def test_main_success(self, mock_subprocess_run, mock_refresh):
        """Test main function with successful refresh."""
        # Mock git repo check
        mock_subprocess_run.return_value = Mock()
        mock_refresh.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            refresh.main()

        assert exc_info.value.code == 0
        mock_refresh.assert_called_once_with(branch="main", remote="origin")

    @patch("refresh.subprocess.run")
    @patch("sys.argv", ["refresh.py"])
    def test_main_not_git_repo(self, mock_subprocess_run):
        """Test main function when not in a git repository."""
        import subprocess

        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git")

        with pytest.raises(SystemExit) as exc_info:
            refresh.main()

        assert exc_info.value.code == 1

    @patch("refresh.refresh_workspace")
    @patch("refresh.subprocess.run")
    @patch("sys.argv", ["refresh.py", "--branch", "develop", "--remote", "upstream"])
    def test_main_custom_args(self, mock_subprocess_run, mock_refresh):
        """Test main function with custom branch and remote."""
        mock_subprocess_run.return_value = Mock()
        mock_refresh.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            refresh.main()

        assert exc_info.value.code == 0
        mock_refresh.assert_called_once_with(branch="develop", remote="upstream")

