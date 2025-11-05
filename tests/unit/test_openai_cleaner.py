"""Unit tests for OpenAICleaner adapter."""

import json
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from cli2ansible.adapters.outbound.llm.openai_cleaner import OpenAICleaner
from cli2ansible.domain.models import Command


@pytest.fixture()
def cleaner() -> OpenAICleaner:
    """Create OpenAICleaner instance."""
    return OpenAICleaner(api_key="test-key-123", model="gpt-4o")


@pytest.fixture()
def sample_commands() -> list[Command]:
    """Create sample commands for testing."""
    session_id = uuid4()
    return [
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


def test_clean_commands_empty_list(cleaner: OpenAICleaner) -> None:
    """Test cleaning with empty command list."""
    session_id = uuid4()

    # Act
    cleaned_commands, report = cleaner.clean_commands([], session_id)

    # Assert
    assert len(cleaned_commands) == 0
    assert report.session_id == session_id
    assert report.original_command_count == 0
    assert report.cleaned_command_count == 0
    assert report.duplicates_removed == 0
    assert report.error_corrections_removed == 0
    assert "No commands" in report.cleaning_rationale


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_clean_commands_calls_api_correctly(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test that clean_commands makes correct API call."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock HTTP client
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "essential_commands": [
                                {
                                    "command": "apt-get install nginx",
                                    "reason": "Install web server",
                                    "is_duplicate": False,
                                    "is_error_correction": False,
                                    "first_occurrence_index": 0,
                                },
                                {
                                    "command": "systemctl start nginx",
                                    "reason": "Start service",
                                    "is_duplicate": False,
                                    "is_error_correction": False,
                                    "first_occurrence_index": 2,
                                },
                            ],
                            "removed_commands": [
                                {
                                    "command": "apt-get install nginx",
                                    "reason": "Duplicate of command 1",
                                    "is_duplicate": True,
                                    "is_error_correction": False,
                                    "original_index": 1,
                                }
                            ],
                            "rationale": "Removed 1 duplicate command",
                        }
                    )
                }
            }
        ]
    }
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act
    cleaned_commands, report = cleaner.clean_commands(sample_commands, session_id)

    # Assert: Verify API call
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"

    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test-key-123"
    assert headers["Content-Type"] == "application/json"

    # Verify payload
    payload = call_args[1]["json"]
    assert payload["model"] == "gpt-4o"
    assert payload["temperature"] == 0.3
    assert payload["response_format"] == {"type": "json_object"}
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    assert (
        payload["messages"][0]["content"]
        == "You are a terminal session analyzer. Respond only with valid JSON."
    )
    assert payload["messages"][1]["role"] == "user"
    assert "apt-get install nginx" in payload["messages"][1]["content"]

    # Verify results
    assert len(cleaned_commands) == 2
    assert cleaned_commands[0].command == "apt-get install nginx"
    assert cleaned_commands[1].command == "systemctl start nginx"
    assert report.duplicates_removed == 1
    assert report.original_command_count == 3
    assert report.cleaned_command_count == 2


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_parse_response_correctly(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test that API response is parsed correctly into domain models."""
    session_id = sample_commands[0].session_id

    # Arrange
    api_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "essential_commands": [
                                {
                                    "command": "apt-get install nginx",
                                    "reason": "Package installation",
                                    "is_duplicate": False,
                                    "is_error_correction": False,
                                    "first_occurrence_index": 0,
                                }
                            ],
                            "removed_commands": [
                                {
                                    "command": "apt-get install nginx",
                                    "reason": "Duplicate",
                                    "is_duplicate": True,
                                    "is_error_correction": False,
                                    "original_index": 1,
                                },
                                {
                                    "command": "systemctl start nginx",
                                    "reason": "Error correction",
                                    "is_duplicate": False,
                                    "is_error_correction": True,
                                    "original_index": 2,
                                },
                            ],
                            "rationale": "Removed 1 duplicate and 1 error correction",
                        }
                    )
                }
            }
        ]
    }

    mock_response = Mock()
    mock_response.json.return_value = api_response
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act
    cleaned_commands, report = cleaner.clean_commands(sample_commands, session_id)

    # Assert: Verify parsed CleanedCommand objects
    assert len(cleaned_commands) == 1
    assert cleaned_commands[0].session_id == session_id
    assert cleaned_commands[0].command == "apt-get install nginx"
    assert cleaned_commands[0].reason == "Package installation"
    assert cleaned_commands[0].first_occurrence == 1.0  # From sample_commands[0]
    assert cleaned_commands[0].is_duplicate is False
    assert cleaned_commands[0].is_error_correction is False

    # Verify parsed CleaningReport
    assert report.session_id == session_id
    assert report.original_command_count == 3
    assert report.cleaned_command_count == 1
    assert report.duplicates_removed == 1
    assert report.error_corrections_removed == 1
    assert report.cleaning_rationale == "Removed 1 duplicate and 1 error correction"


def test_build_prompt_includes_all_commands(cleaner: OpenAICleaner) -> None:
    """Test that prompt includes all commands with metadata."""
    session_id = uuid4()
    commands = [
        Command(
            session_id=session_id,
            raw="echo hello",
            normalized="echo hello",
            timestamp=1.5,
        ),
        Command(
            session_id=session_id,
            raw="echo world",
            normalized="echo world",
            timestamp=2.5,
        ),
    ]

    # Act
    prompt = cleaner._build_prompt(commands)

    # Assert
    assert "1. echo hello (timestamp: 1.5)" in prompt
    assert "2. echo world (timestamp: 2.5)" in prompt
    assert "duplicate" in prompt.lower()
    assert "error correction" in prompt.lower()
    assert "JSON" in prompt


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_api_http_status_error(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test handling of HTTP status errors from OpenAI API."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock 401 unauthorized error
    import httpx

    mock_response = Mock()
    mock_response.status_code = 401
    mock_client = Mock()
    mock_client.post.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=Mock(), response=mock_response
    )
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act & Assert
    with pytest.raises(RuntimeError, match="OpenAI API request failed with status 401"):
        cleaner.clean_commands(sample_commands, session_id)


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_api_timeout_error(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test handling of timeout errors from OpenAI API."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock timeout
    import httpx

    mock_client = Mock()
    mock_client.post.side_effect = httpx.TimeoutException("Request timed out")
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act & Assert
    with pytest.raises(RuntimeError, match="OpenAI API request timed out"):
        cleaner.clean_commands(sample_commands, session_id)


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_api_general_exception(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test handling of general exceptions from OpenAI API."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock generic exception
    mock_client = Mock()
    mock_client.post.side_effect = Exception("Something went wrong")
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to call OpenAI API"):
        cleaner.clean_commands(sample_commands, session_id)


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_parse_response_empty_choices(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test handling of empty choices in API response."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock response with empty choices
    mock_response = Mock()
    mock_response.json.return_value = {"choices": []}
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act & Assert
    with pytest.raises(ValueError, match="Empty response from API"):
        cleaner.clean_commands(sample_commands, session_id)


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_parse_response_empty_content(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test handling of empty content in API response."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock response with empty content
    mock_response = Mock()
    mock_response.json.return_value = {"choices": [{"message": {"content": ""}}]}
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act & Assert
    with pytest.raises(ValueError, match="Empty content in API response"):
        cleaner.clean_commands(sample_commands, session_id)


@patch("cli2ansible.adapters.outbound.llm.openai_cleaner.httpx.Client")
def test_client_timeout_configuration(
    mock_client_class: Mock, cleaner: OpenAICleaner, sample_commands: list[Command]
) -> None:
    """Test that HTTP client is configured with correct timeout."""
    session_id = sample_commands[0].session_id

    # Arrange: Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "essential_commands": [],
                            "removed_commands": [],
                            "rationale": "Test",
                        }
                    )
                }
            }
        ]
    }
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client_class.return_value = mock_client

    # Act
    cleaner.clean_commands(sample_commands, session_id)

    # Assert: Verify client created with timeout
    mock_client_class.assert_called_once_with(timeout=60.0)
