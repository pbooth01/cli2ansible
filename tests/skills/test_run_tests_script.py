"""Tests for .augment/skills/run-tests/scripts/run_tests.py"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the script directory to the path
script_path = Path(__file__).parent.parent.parent / ".augment/skills/run-tests/scripts"
sys.path.insert(0, str(script_path))

import run_tests


class TestCheckPoetryAvailable:
    """Tests for check_poetry_available function."""

    @patch("run_tests.subprocess.run")
    def test_poetry_available(self, mock_run):
        """Test when poetry is available."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.check_poetry_available()

        assert result is True
        mock_run.assert_called_once_with(
            ["poetry", "--version"], capture_output=True, check=False
        )

    @patch("run_tests.subprocess.run")
    def test_poetry_not_available(self, mock_run):
        """Test when poetry is not available."""
        mock_run.side_effect = FileNotFoundError()

        result = run_tests.check_poetry_available()

        assert result is False


class TestRunTests:
    """Tests for run_tests function."""

    @patch("run_tests.subprocess.run")
    def test_run_tests_default(self, mock_run, capsys):
        """Test running tests with default options."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests()

        assert result == 0
        captured = capsys.readouterr()
        assert "Running all tests" in captured.out

    @patch("run_tests.subprocess.run")
    def test_run_tests_unit_only(self, mock_run, capsys):
        """Test running unit tests only."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(unit_only=True)

        assert result == 0
        # Check that -m "not integration" is in the command
        call_args = mock_run.call_args[0][0]
        assert "-m" in call_args
        assert "not integration" in call_args
        captured = capsys.readouterr()
        assert "unit tests only" in captured.out

    @patch("run_tests.subprocess.run")
    def test_run_tests_integration_only(self, mock_run, capsys):
        """Test running integration tests only."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(integration_only=True)

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "-m" in call_args
        assert "integration" in call_args

    @patch("run_tests.Path")
    @patch("run_tests.subprocess.run")
    def test_run_tests_with_file(self, mock_run, mock_path, capsys):
        """Test running tests for a specific file."""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(file_path="tests/test_example.py")

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "tests/test_example.py" in call_args

    @patch("run_tests.Path")
    def test_run_tests_file_not_found(self, mock_path, capsys):
        """Test running tests with non-existent file."""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        result = run_tests.run_tests(file_path="tests/missing.py")

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out

    @patch("run_tests.subprocess.run")
    def test_run_tests_with_coverage(self, mock_run, capsys):
        """Test running tests with coverage."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(coverage=True)

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "--cov=src" in call_args
        captured = capsys.readouterr()
        assert "Coverage: enabled" in captured.out

    @patch("run_tests.subprocess.run")
    def test_run_tests_with_pattern(self, mock_run, capsys):
        """Test running tests with pattern."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(test_pattern="test_example")

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "-k" in call_args
        assert "test_example" in call_args

    @patch("run_tests.subprocess.run")
    def test_run_tests_verbose(self, mock_run):
        """Test running tests in verbose mode."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(verbose=True)

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "-v" in call_args

    @patch("run_tests.subprocess.run")
    def test_run_tests_fail_fast(self, mock_run, capsys):
        """Test running tests with fail fast."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_tests.run_tests(fail_fast=True)

        assert result == 0
        call_args = mock_run.call_args[0][0]
        assert "-x" in call_args
        captured = capsys.readouterr()
        assert "Fail fast: enabled" in captured.out

