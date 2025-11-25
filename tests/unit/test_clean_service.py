"""Unit tests for CleanSession application service."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from cli2ansible.application import CleanSessionService, CommandExtractionService
from cli2ansible.domain.entities import CleanedCommand, CleaningReport, Command
from cli2ansible.domain.ports import LLMPort, SessionRepositoryPort


@pytest.fixture()
def mock_repo() -> Mock:
    """Create mock repository."""
    return Mock(spec=SessionRepositoryPort)


@pytest.fixture()
def mock_llm() -> Mock:
    """Create mock LLM port."""
    return Mock(spec=LLMPort)


@pytest.fixture()
def mock_extractor() -> Mock:
    """Create mock command extraction service."""
    return Mock(spec=CommandExtractionService)


@pytest.fixture()
def clean_service(
    mock_repo: Mock, mock_llm: Mock, mock_extractor: Mock
) -> CleanSessionService:
    """Create CleanSessionService with mocked dependencies."""
    return CleanSessionService(mock_repo, mock_llm, mock_extractor)


def test_clean_with_valid_session(
    clean_service: CleanSessionService, mock_repo: Mock, mock_llm: Mock
) -> None:
    """Test cleaning commands for a session with commands."""
    from cli2ansible.domain.entities import Session, SessionStatus

    session_id = uuid4()

    # Arrange: Mock session and commands in repository
    mock_session = Session(id=session_id, name="test", status=SessionStatus.UPLOADED)
    mock_repo.get.return_value = mock_session

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
    result = clean_service.clean(session_id)

    # Assert
    mock_repo.get.assert_called_once_with(session_id)
    mock_repo.get_commands.assert_called_once_with(session_id)
    mock_llm.clean_commands.assert_called_once_with(mock_commands, session_id)
    assert len(result.cleaned_commands) == 2
    assert result.cleaned_commands[0].command == "apt-get install nginx"
    assert result.cleaned_commands[0].occurrence_count == 2
    assert result.report.duplicates_removed == 1
    assert result.report.original_command_count == 3
    assert result.report.cleaned_command_count == 2


def test_clean_with_empty_session(
    clean_service: CleanSessionService, mock_repo: Mock, mock_llm: Mock
) -> None:
    """Test cleaning commands when session has no commands."""
    from cli2ansible.application.errors import BadRequestError
    from cli2ansible.domain.entities import Session, SessionStatus

    session_id = uuid4()

    # Arrange: Mock session with no commands
    mock_session = Session(id=session_id, name="test", status=SessionStatus.UPLOADED)
    mock_repo.get.return_value = mock_session
    mock_repo.get_commands.return_value = []
    mock_repo.get_events.return_value = []

    # Act & Assert - should raise BadRequestError
    with pytest.raises(BadRequestError, match="No commands to clean"):
        clean_service.clean(session_id)
