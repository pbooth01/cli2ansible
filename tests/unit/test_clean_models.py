"""Unit tests for cleaning-related domain models."""

from datetime import datetime
from uuid import uuid4

from cli2ansible.domain.models import CleanedCommand, CleaningReport


def test_cleaned_command_creation() -> None:
    """Test creating a CleanedCommand."""
    session_id = uuid4()
    cmd = CleanedCommand(
        session_id=session_id,
        command="apt-get install nginx",
        reason="Essential for web server setup",
        first_occurrence=1.0,
        occurrence_count=1,
        is_duplicate=False,
        is_error_correction=False,
    )

    assert cmd.session_id == session_id
    assert cmd.command == "apt-get install nginx"
    assert cmd.reason == "Essential for web server setup"
    assert cmd.first_occurrence == 1.0
    assert cmd.occurrence_count == 1
    assert cmd.is_duplicate is False
    assert cmd.is_error_correction is False


def test_cleaned_command_with_duplicate_flag() -> None:
    """Test creating a CleanedCommand marked as duplicate."""
    session_id = uuid4()
    cmd = CleanedCommand(
        session_id=session_id,
        command="echo test",
        reason="Duplicate of earlier command",
        first_occurrence=5.0,
        occurrence_count=3,
        is_duplicate=True,
        is_error_correction=False,
    )

    assert cmd.is_duplicate is True
    assert cmd.occurrence_count == 3


def test_cleaned_command_with_error_correction_flag() -> None:
    """Test creating a CleanedCommand marked as error correction."""
    session_id = uuid4()
    cmd = CleanedCommand(
        session_id=session_id,
        command="apt-get instal nginx",
        reason="Typo corrected in next command",
        first_occurrence=2.0,
        occurrence_count=1,
        is_duplicate=False,
        is_error_correction=True,
    )

    assert cmd.is_error_correction is True


def test_cleaning_report_creation() -> None:
    """Test creating a CleaningReport."""
    session_id = uuid4()
    report = CleaningReport(
        session_id=session_id,
        original_command_count=10,
        cleaned_command_count=6,
        duplicates_removed=3,
        error_corrections_removed=1,
        cleaning_rationale="Removed 3 duplicates and 1 typo correction",
    )

    assert report.session_id == session_id
    assert report.original_command_count == 10
    assert report.cleaned_command_count == 6
    assert report.duplicates_removed == 3
    assert report.error_corrections_removed == 1
    assert report.cleaning_rationale == "Removed 3 duplicates and 1 typo correction"
    assert isinstance(report.generated_at, datetime)


def test_cleaning_report_with_zeros() -> None:
    """Test creating a CleaningReport with no removals."""
    session_id = uuid4()
    report = CleaningReport(
        session_id=session_id,
        original_command_count=5,
        cleaned_command_count=5,
        duplicates_removed=0,
        error_corrections_removed=0,
        cleaning_rationale="All commands are unique and valid",
    )

    assert report.duplicates_removed == 0
    assert report.error_corrections_removed == 0
    assert report.original_command_count == report.cleaned_command_count
