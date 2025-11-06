"""Unit tests for CLI functions."""

import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from cli2ansible.cli import convert_cast_to_json, main


class TestConvertCastToJson:
    """Test suite for convert_cast_to_json function."""

    def test_convert_cast_to_json_stdout(self) -> None:
        """Test converting .cast file outputs to stdout."""
        # Arrange - use OSC sequences
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;ls\\u0007"]\n'
            '[1.0,"i","\\r"]\n'
            '[1.5,"o","\\u001b]2;pwd\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Capture stdout
            captured_output = StringIO()

            # Act
            with patch("sys.stdout", captured_output):
                convert_cast_to_json(temp_path)

            # Assert
            output = captured_output.getvalue()
            parsed = json.loads(output)
            assert len(parsed) == 2
            assert parsed[0]["event_type"] == "o"
            assert parsed[0]["data"] == "ls"
            assert parsed[0]["timestamp"] == 0.0  # Normalized
            assert parsed[0]["sequence"] == 0
            assert parsed[1]["event_type"] == "o"
            assert parsed[1]["data"] == "pwd"
        finally:
            Path(temp_path).unlink()

    def test_convert_cast_to_json_file(self) -> None:
        """Test converting .cast file writes to output file."""
        # Arrange - use OSC sequence
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;echo hello\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            cast_path = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            # Act
            captured_stderr = StringIO()
            with patch("sys.stderr", captured_stderr):
                convert_cast_to_json(cast_path, output_path)

            # Assert
            assert Path(output_path).exists()
            content = Path(output_path).read_text(encoding="utf-8")
            parsed = json.loads(content)
            assert len(parsed) == 1
            assert parsed[0]["event_type"] == "o"
            assert parsed[0]["data"] == "echo hello"

            # Check stderr message
            stderr_output = captured_stderr.getvalue()
            assert "Converted 1 events to" in stderr_output
            assert output_path in stderr_output
        finally:
            Path(cast_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_convert_cast_to_json_file_not_found(self) -> None:
        """Test converting non-existent file raises FileNotFoundError."""
        # Arrange
        nonexistent_path = "/tmp/nonexistent_12345.cast"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            convert_cast_to_json(nonexistent_path)

    def test_convert_cast_to_json_invalid_format(self) -> None:
        """Test converting invalid .cast file raises ValueError."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write("invalid content")
            temp_path = f.name

        try:
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid JSON header"):
                convert_cast_to_json(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_convert_cast_to_json_pretty_print(self) -> None:
        """Test JSON output is pretty-printed with indentation."""
        # Arrange - use OSC sequence
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;test\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                convert_cast_to_json(temp_path)

            # Assert
            output = captured_output.getvalue()
            # Pretty-printed JSON should contain newlines and spaces
            assert "\n" in output
            assert "  " in output  # 2-space indent
        finally:
            Path(temp_path).unlink()

    def test_convert_cast_to_json_excludes_session_id(self) -> None:
        """Test JSON output excludes session_id field."""
        # Arrange - use OSC sequence
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;test\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                convert_cast_to_json(temp_path)

            # Assert
            output = captured_output.getvalue()
            parsed = json.loads(output)
            assert "session_id" not in parsed[0]
            assert "timestamp" in parsed[0]
            assert "event_type" in parsed[0]
            assert "data" in parsed[0]
            assert "sequence" in parsed[0]
        finally:
            Path(temp_path).unlink()


class TestCLIMain:
    """Test suite for CLI main function."""

    def test_cli_main_convert_cast_stdout(self) -> None:
        """Test CLI with convert-cast command outputs to stdout."""
        # Arrange - use OSC sequence
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;cli test\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            temp_path = f.name

        try:
            # Act
            captured_output = StringIO()
            with patch("sys.argv", ["cli2ansible", "convert-cast", temp_path]), patch(
                "sys.stdout", captured_output
            ):
                main()

            # Assert
            output = captured_output.getvalue()
            parsed = json.loads(output)
            assert len(parsed) == 1
            assert parsed[0]["data"] == "cli test"
        finally:
            Path(temp_path).unlink()

    def test_cli_main_convert_cast_file_output(self) -> None:
        """Test CLI with convert-cast and -o flag writes to file."""
        # Arrange - use OSC sequence
        cast_content = (
            '{"version":3,"timestamp":1234567890}\n'
            '[0.0,"i","\\r"]\n'
            '[0.5,"o","\\u001b]2;file test\\u0007"]\n'
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            cast_path = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            # Act
            with patch(
                "sys.argv",
                ["cli2ansible", "convert-cast", cast_path, "-o", output_path],
            ):
                main()

            # Assert
            assert Path(output_path).exists()
            content = Path(output_path).read_text(encoding="utf-8")
            parsed = json.loads(content)
            assert parsed[0]["data"] == "file test"
        finally:
            Path(cast_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_cli_main_file_not_found(self) -> None:
        """Test CLI with missing file exits with code 1."""
        # Arrange
        nonexistent_path = "/tmp/nonexistent_12345.cast"

        # Act & Assert
        captured_stderr = StringIO()
        with patch(
            "sys.argv", ["cli2ansible", "convert-cast", nonexistent_path]
        ), patch("sys.stderr", captured_stderr), pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        stderr_output = captured_stderr.getvalue()
        assert "Error: File not found" in stderr_output
        assert nonexistent_path in stderr_output

    def test_cli_main_invalid_format(self) -> None:
        """Test CLI with invalid .cast file exits with code 1."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write("invalid format")
            temp_path = f.name

        try:
            # Act & Assert
            captured_stderr = StringIO()
            with patch("sys.argv", ["cli2ansible", "convert-cast", temp_path]), patch(
                "sys.stderr", captured_stderr
            ), pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            stderr_output = captured_stderr.getvalue()
            assert "Error: Invalid .cast file" in stderr_output
        finally:
            Path(temp_path).unlink()

    def test_cli_main_no_command(self) -> None:
        """Test CLI without command shows help and exits."""
        # Act & Assert
        with patch("sys.argv", ["cli2ansible"]), pytest.raises(SystemExit):
            main()

    def test_cli_main_help(self) -> None:
        """Test CLI with --help shows usage."""
        # Act & Assert
        with patch(
            "sys.argv", ["cli2ansible", "convert-cast", "--help"]
        ), pytest.raises(SystemExit) as exc_info:
            main()

        # Help should exit with code 0
        assert exc_info.value.code == 0

    def test_cli_main_output_long_flag(self) -> None:
        """Test CLI with --output long flag for output."""
        # Arrange
        cast_content = '{"version":3,"timestamp":1234567890}\n[0.0,"o","test"]\n'

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write(cast_content)
            cast_path = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            # Act
            with patch(
                "sys.argv",
                ["cli2ansible", "convert-cast", cast_path, "--output", output_path],
            ):
                main()

            # Assert
            assert Path(output_path).exists()
        finally:
            Path(cast_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_cli_main_generic_exception(self) -> None:
        """Test CLI handles unexpected exceptions gracefully."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cast", delete=False) as f:
            f.write('{"version":3}\n[0.0,"o","test"]')
            temp_path = f.name

        try:
            # Act & Assert
            captured_stderr = StringIO()
            with patch("sys.argv", ["cli2ansible", "convert-cast", temp_path]), patch(
                "cli2ansible.cli.parse_cast_file",
                side_effect=RuntimeError("Unexpected error"),
            ), patch("sys.stderr", captured_stderr), pytest.raises(
                SystemExit
            ) as exc_info:
                main()

            assert exc_info.value.code == 1
            stderr_output = captured_stderr.getvalue()
            assert "Error: Unexpected error" in stderr_output
        finally:
            Path(temp_path).unlink()
