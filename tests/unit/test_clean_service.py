"""Unit tests for CleanSession domain service."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from cli2ansible.domain.models import CleanedCommand, CleaningReport, Command
from cli2ansible.domain.ports import LLMPort, SessionRepositoryPort
from cli2ansible.domain.services import CleanSession


@pytest.fixture()
def mock_repo() -> Mock:
    """Create mock repository."""
    return Mock(spec=SessionRepositoryPort)


@pytest.fixture()
def mock_llm() -> Mock:
    """Create mock LLM port."""
    return Mock(spec=LLMPort)


@pytest.fixture()
def clean_service(mock_repo: Mock, mock_llm: Mock) -> CleanSession:
    """Create CleanSession service with mocked dependencies."""
    return CleanSession(mock_repo, mock_llm)


def test_clean_commands_with_valid_session(
    clean_service: CleanSession, mock_repo: Mock, mock_llm: Mock
) -> None:
    """Test cleaning commands for a session with commands."""
    session_id = uuid4()

    # Arrange: Mock commands in repository
    mock_commands = [
        Command(
            session_id=session_id,
            raw="apt-get install nginx",
            normalized="apt-get install nginx",
            timestamp=1.0,
        ),
        Command(
            session_id=session_id,
            raw="apt-get install nginx",
            normalized="apt-get install nginx",
            timestamp=2.0,
        ),
        Command(
            session_id=session_id,
            raw="systemctl start nginx",
            normalized="systemctl start nginx",
            timestamp=3.0,
        ),
    ]
    mock_repo.get_commands.return_value = mock_commands

    # Mock LLM response
    expected_cleaned = [
        CleanedCommand(
            session_id=session_id,
            command="apt-get install nginx",
            reason="Install web server",
            first_occurrence=1.0,
            occurrence_count=2,
            is_duplicate=False,
            is_error_correction=False,
        ),
        CleanedCommand(
            session_id=session_id,
            command="systemctl start nginx",
            reason="Start web server",
            first_occurrence=3.0,
            occurrence_count=1,
            is_duplicate=False,
            is_error_correction=False,
        ),
    ]
    expected_report = CleaningReport(
        session_id=session_id,
        original_command_count=3,
        cleaned_command_count=2,
        duplicates_removed=1,
        error_corrections_removed=0,
        cleaning_rationale="Removed 1 duplicate command",
    )
    mock_llm.clean_commands.return_value = (expected_cleaned, expected_report)

    # Act
    cleaned_commands, report = clean_service.clean_commands(session_id)

    # Assert
    mock_repo.get_commands.assert_called_once_with(session_id)
    mock_llm.clean_commands.assert_called_once_with(mock_commands, session_id)
    assert len(cleaned_commands) == 2
    assert cleaned_commands[0].command == "apt-get install nginx"
    assert cleaned_commands[0].occurrence_count == 2
    assert report.duplicates_removed == 1
    assert report.original_command_count == 3
    assert report.cleaned_command_count == 2


def test_clean_commands_with_empty_session(
    clean_service: CleanSession, mock_repo: Mock, mock_llm: Mock
) -> None:
    """Test cleaning commands when session has no commands."""
    session_id = uuid4()

    # Arrange: Empty command list
    mock_repo.get_commands.return_value = []

    # Act
    cleaned_commands, report = clean_service.clean_commands(session_id)

    # Assert
    mock_repo.get_commands.assert_called_once_with(session_id)
    mock_llm.clean_commands.assert_not_called()  # Should not call LLM for empty list
    assert len(cleaned_commands) == 0
    assert report.session_id == session_id
    assert report.original_command_count == 0
    assert report.cleaned_command_count == 0
    assert report.duplicates_removed == 0
    assert report.error_corrections_removed == 0
    assert "No commands" in report.cleaning_rationale


def test_get_essential_commands_filters_duplicates(
    clean_service: CleanSession, mock_repo: Mock, mock_llm: Mock
) -> None:
    """Test get_essential_commands filters out duplicates."""
    session_id = uuid4()

    # Arrange
    mock_commands = [
        Command(
            session_id=session_id,
            raw="echo test",
            normalized="echo test",
            timestamp=1.0,
        ),
    ]
    mock_repo.get_commands.return_value = mock_commands

    cleaned_with_duplicates = [
        CleanedCommand(
            session_id=session_id,
            command="apt-get install nginx",
            reason="Install web server",
            first_occurrence=1.0,
            occurrence_count=1,
            is_duplicate=False,
            is_error_correction=False,
        ),
        CleanedCommand(
            session_id=session_id,
            command="apt-get install nginx",
            reason="Duplicate",
            first_occurrence=1.0,
            occurrence_count=2,
            is_duplicate=True,
            is_error_correction=False,
        ),
        CleanedCommand(
            session_id=session_id,
            command="systemctl start nginx",
            reason="Start service",
            first_occurrence=3.0,
            occurrence_count=1,
            is_duplicate=False,
            is_error_correction=False,
        ),
    ]
    mock_report = CleaningReport(
        session_id=session_id,
        original_command_count=3,
        cleaned_command_count=3,
        duplicates_removed=0,
        error_corrections_removed=0,
        cleaning_rationale="Test",
    )
    mock_llm.clean_commands.return_value = (cleaned_with_duplicates, mock_report)

    # Act
    essential = clean_service.get_essential_commands(session_id)

    # Assert
    assert len(essential) == 2  # Should exclude the duplicate
    assert "apt-get install nginx" in essential
    assert "systemctl start nginx" in essential
