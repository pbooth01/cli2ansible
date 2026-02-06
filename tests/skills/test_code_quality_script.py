"""Tests for .augment/skills/code-quality/scripts/check.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/code-quality/scripts"
sys.path.insert(0, str(script_path))

import check


class TestRunCommand:
    """Tests for run_command function."""

    @patch("check.subprocess.run")
    def test_run_command_success(self, mock_run, capsys):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = check.run_command(["echo", "test"], "Test command")

        assert result is True
        mock_run.assert_called_once_with(["echo", "test"])
        captured = capsys.readouterr()
        assert "Test command" in captured.out

    @patch("check.subprocess.run")
    def test_run_command_failure(self, mock_run, capsys):
        """Test failed command execution."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = check.run_command(["false"], "Failing command")

        assert result is False


class TestRunRuff:
    """Tests for run_ruff function."""

    @patch("check.run_command")
    def test_run_ruff_default(self, mock_run_command):
        """Test ruff with default options."""
        mock_run_command.return_value = True

        result = check.run_ruff()

        assert result is True
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        assert args == ["poetry", "run", "ruff", "check", "."]

    @patch("check.run_command")
    def test_run_ruff_with_fix(self, mock_run_command):
        """Test ruff with --fix option."""
        mock_run_command.return_value = True

        result = check.run_ruff(fix=True)

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "--fix" in args

    @patch("check.run_command")
    def test_run_ruff_with_file_path(self, mock_run_command):
        """Test ruff with specific file path."""
        mock_run_command.return_value = True

        result = check.run_ruff(file_path="src/test.py")

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "src/test.py" in args
        assert "." not in args


class TestRunMypy:
    """Tests for run_mypy function."""

    @patch("check.run_command")
    def test_run_mypy_default(self, mock_run_command):
        """Test mypy with default options."""
        mock_run_command.return_value = True

        result = check.run_mypy()

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert args == ["poetry", "run", "mypy", "src"]

    @patch("check.run_command")
    def test_run_mypy_with_file_path(self, mock_run_command):
        """Test mypy with specific file path."""
        mock_run_command.return_value = True

        result = check.run_mypy(file_path="src/test.py")

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "src/test.py" in args
        assert "src" not in args


class TestRunBlack:
    """Tests for run_black function."""

    @patch("check.run_command")
    def test_run_black_check_mode(self, mock_run_command):
        """Test black in check mode (default)."""
        mock_run_command.return_value = True

        result = check.run_black()

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "--check" in args

    @patch("check.run_command")
    def test_run_black_fix_mode(self, mock_run_command):
        """Test black in fix mode."""
        mock_run_command.return_value = True

        result = check.run_black(fix=True)

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "--check" not in args

    @patch("check.run_command")
    def test_run_black_with_file_path(self, mock_run_command):
        """Test black with specific file path."""
        mock_run_command.return_value = True

        result = check.run_black(file_path="src/test.py")

        assert result is True
        args = mock_run_command.call_args[0][0]
        assert "src/test.py" in args


class TestMain:
    """Tests for main function."""

    @patch("check.run_ruff")
    @patch("check.run_mypy")
    @patch("check.run_black")
    @patch("sys.argv", ["check.py"])
    def test_main_all_checks(self, mock_black, mock_mypy, mock_ruff):
        """Test running all checks (default behavior)."""
        mock_ruff.return_value = True
        mock_mypy.return_value = True
        mock_black.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            check.main()

        assert exc_info.value.code == 0
        mock_ruff.assert_called_once()
        mock_mypy.assert_called_once()
        mock_black.assert_called_once()

    @patch("check.run_ruff")
    @patch("check.run_mypy")
    @patch("check.run_black")
    @patch("sys.argv", ["check.py", "--lint"])
    def test_main_lint_only(self, mock_black, mock_mypy, mock_ruff):
        """Test running only linting."""
        mock_ruff.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            check.main()

        assert exc_info.value.code == 0
        mock_ruff.assert_called_once()
        mock_mypy.assert_not_called()
        mock_black.assert_not_called()

