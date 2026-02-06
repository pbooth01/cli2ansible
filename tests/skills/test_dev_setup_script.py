"""Tests for .augment/skills/dev-setup/scripts/setup.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/dev-setup/scripts"
sys.path.insert(0, str(script_path))

import setup


class TestRunCommand:
    """Tests for run_command function."""

    @patch("setup.subprocess.run")
    def test_run_command_success(self, mock_run, capsys):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, result = setup.run_command(["echo", "test"], "Test command")

        assert success is True
        assert result == mock_result
        captured = capsys.readouterr()
        assert "Test command" in captured.out

    @patch("setup.subprocess.run")
    def test_run_command_failure(self, mock_run, capsys):
        """Test failed command execution."""
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Error message"
        )

        success, result = setup.run_command(["false"], "Failing command")

        assert success is False
        captured = capsys.readouterr()
        assert "Error" in captured.out


class TestCheckPrerequisites:
    """Tests for check_prerequisites function."""

    @patch("setup.run_command")
    def test_check_prerequisites_success(self, mock_run_command, capsys):
        """Test successful prerequisites check."""
        # Mock Poetry check
        mock_run_command.return_value = (True, Mock())

        result = setup.check_prerequisites()

        assert result is True
        captured = capsys.readouterr()
        assert "Python" in captured.out
        assert "Poetry" in captured.out

    @patch("setup.run_command")
    def test_check_prerequisites_no_poetry(self, mock_run_command, capsys):
        """Test prerequisites check when Poetry is missing."""
        # Mock Poetry check to fail
        mock_run_command.return_value = (False, Mock())

        result = setup.check_prerequisites()

        assert result is False
        captured = capsys.readouterr()
        assert "Poetry not found" in captured.out

    @patch("sys.version_info", (3, 10, 0, "final", 0))
    def test_check_prerequisites_old_python(self, capsys):
        """Test prerequisites check with old Python version."""
        result = setup.check_prerequisites()

        assert result is False
        captured = capsys.readouterr()
        assert "Python 3.11+ required" in captured.out


class TestInstallDependencies:
    """Tests for install_dependencies function."""

    @patch("setup.run_command")
    def test_install_dependencies_success(self, mock_run_command, capsys):
        """Test successful dependency installation."""
        mock_run_command.return_value = (True, Mock())

        result = setup.install_dependencies()

        assert result is True
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        assert args == ["poetry", "install"]

    @patch("setup.shutil.rmtree")
    @patch("setup.Path")
    @patch("setup.run_command")
    def test_install_dependencies_clean(self, mock_run_command, mock_path, mock_rmtree, capsys):
        """Test dependency installation with clean flag."""
        # Mock .venv path
        mock_venv = Mock()
        mock_venv.exists.return_value = True
        mock_path.return_value = mock_venv

        mock_run_command.return_value = (True, Mock())

        result = setup.install_dependencies(clean=True)

        assert result is True
        mock_rmtree.assert_called_once()
        captured = capsys.readouterr()
        assert "Removing existing virtual environment" in captured.out

    @patch("setup.run_command")
    def test_install_dependencies_failure(self, mock_run_command):
        """Test failed dependency installation."""
        mock_run_command.return_value = (False, Mock())

        result = setup.install_dependencies()

        assert result is False


class TestStartDockerServices:
    """Tests for start_docker_services function."""

    @patch("setup.time.sleep")
    @patch("setup.run_command")
    def test_start_docker_services_success(self, mock_run_command, mock_sleep, capsys):
        """Test successful Docker services start."""
        mock_run_command.return_value = (True, Mock())

        result = setup.start_docker_services()

        assert result is True
        # Should call docker compose up
        assert any("up" in str(call) for call in mock_run_command.call_args_list)

    @patch("setup.run_command")
    def test_start_docker_services_failure(self, mock_run_command):
        """Test failed Docker services start."""
        mock_run_command.return_value = (False, Mock())

        result = setup.start_docker_services()

        assert result is False


class TestRunMigrations:
    """Tests for run_migrations function."""

    @patch("setup.run_command")
    def test_run_migrations_success(self, mock_run_command, capsys):
        """Test successful database migrations."""
        mock_run_command.return_value = (True, Mock())

        result = setup.run_migrations()

        assert result is True
        # Should call alembic upgrade head
        args = mock_run_command.call_args[0][0]
        assert "alembic" in args or "upgrade" in str(args)

    @patch("setup.run_command")
    def test_run_migrations_failure(self, mock_run_command):
        """Test failed database migrations."""
        mock_run_command.return_value = (False, Mock())

        result = setup.run_migrations()

        assert result is False


class TestMain:
    """Tests for main function."""

    @patch("setup.run_migrations")
    @patch("setup.start_docker_services")
    @patch("setup.install_dependencies")
    @patch("setup.check_prerequisites")
    @patch("sys.argv", ["setup.py"])
    def test_main_success(
        self, mock_prereqs, mock_install, mock_docker, mock_migrations
    ):
        """Test main function with successful setup."""
        mock_prereqs.return_value = True
        mock_install.return_value = True
        mock_docker.return_value = True
        mock_migrations.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            setup.main()

        assert exc_info.value.code == 0

    @patch("setup.check_prerequisites")
    @patch("sys.argv", ["setup.py"])
    def test_main_prerequisites_fail(self, mock_prereqs):
        """Test main function when prerequisites check fails."""
        mock_prereqs.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            setup.main()

        assert exc_info.value.code == 1

