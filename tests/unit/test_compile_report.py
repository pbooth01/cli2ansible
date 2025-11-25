"""Unit tests for compile service enhanced reporting."""


import pytest
from cli2ansible.adapters.outbound.db.repository import SQLAlchemyRepository
from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.adapters.outbound.translator.rules_engine import RulesEngine
from cli2ansible.application import (
    CommandExtractionService,
    CompilePlaybookService,
    IngestSessionService,
)
from cli2ansible.domain.entities import Command


@pytest.fixture()
def repo() -> SQLAlchemyRepository:
    """Create in-memory repository for testing."""
    repo = SQLAlchemyRepository("sqlite:///:memory:")
    repo.create_tables()
    return repo


@pytest.fixture()
def extractor(repo: SQLAlchemyRepository) -> CommandExtractionService:
    """Create CommandExtractionService."""
    return CommandExtractionService(repo)


@pytest.fixture()
def ingest_service(
    repo: SQLAlchemyRepository, extractor: CommandExtractionService
) -> IngestSessionService:
    """Create IngestSessionService."""
    return IngestSessionService(repo, extractor)


@pytest.fixture()
def compile_service(
    repo: SQLAlchemyRepository, extractor: CommandExtractionService
) -> CompilePlaybookService:
    """Create CompilePlaybookService with mock dependencies."""
    from cli2ansible.domain.ports import ObjectStorePort

    class MockObjectStore(ObjectStorePort):
        """Mock object store."""

        def upload(
            self, key: str, data: bytes, content_type: str = "application/octet-stream"
        ) -> str:
            return key

        def download(self, key: str) -> bytes:
            return b""

        def delete(self, key: str) -> None:
            pass

        def generate_url(self, key: str, expires_in: int = 3600) -> str:
            return f"http://mock/{key}"

    translator = RulesEngine()
    generator = AnsibleRoleGenerator()
    store = MockObjectStore()
    return CompilePlaybookService(repo, translator, generator, store, extractor)


def test_compile_report_includes_module_breakdown(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report includes module breakdown statistics."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create commands with different modules
    commands = [
        Command(
            session_id=session_id,
            raw="apt-get install -y nginx",
            normalized="apt-get install -y nginx",
            sudo=True,
            timestamp=1.0,
        ),
        Command(
            session_id=session_id,
            raw="apt-get install -y curl",
            normalized="apt-get install -y curl",
            sudo=True,
            timestamp=2.0,
        ),
        Command(
            session_id=session_id,
            raw="systemctl start nginx",
            normalized="systemctl start nginx",
            sudo=True,
            timestamp=3.0,
        ),
        Command(
            session_id=session_id,
            raw="mkdir -p /var/www",
            normalized="mkdir -p /var/www",
            timestamp=4.0,
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify module breakdown
    assert "apt" in report.module_breakdown
    assert report.module_breakdown["apt"] == 2
    assert "systemd" in report.module_breakdown
    assert report.module_breakdown["systemd"] == 1
    assert "file" in report.module_breakdown
    assert report.module_breakdown["file"] == 1


def test_compile_report_includes_quality_percentages(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report includes quality percentage calculations."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create commands with different confidence levels
    commands = [
        # High confidence (apt)
        Command(
            session_id=session_id,
            raw="apt-get install -y nginx",
            normalized="apt-get install -y nginx",
            timestamp=1.0,
        ),
        Command(
            session_id=session_id,
            raw="apt-get install -y curl",
            normalized="apt-get install -y curl",
            timestamp=2.0,
        ),
        # Low confidence (unknown command -> shell)
        Command(
            session_id=session_id,
            raw="some-unknown-command",
            normalized="some-unknown-command",
            timestamp=3.0,
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify percentages (2 high, 1 low out of 3 total)
    assert report.high_confidence == 2
    assert report.low_confidence == 1
    assert report.high_confidence_percentage == pytest.approx(66.67, abs=0.01)
    assert report.low_confidence_percentage == pytest.approx(33.33, abs=0.01)
    assert report.medium_confidence_percentage == 0.0


def test_compile_report_includes_session_duration(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report includes session duration calculation."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create commands with different timestamps
    commands = [
        Command(
            session_id=session_id,
            raw="apt-get update",
            normalized="apt-get update",
            timestamp=10.5,
        ),
        Command(
            session_id=session_id,
            raw="apt-get install nginx",
            normalized="apt-get install nginx",
            timestamp=25.3,
        ),
        Command(
            session_id=session_id,
            raw="systemctl start nginx",
            normalized="systemctl start nginx",
            timestamp=45.8,
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify duration (45.8 - 10.5 = 35.3)
    assert report.session_duration_seconds == pytest.approx(35.3, abs=0.01)


def test_compile_report_includes_most_common_commands(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report includes most common commands."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create commands with some duplicates
    commands = [
        Command(
            session_id=session_id,
            raw="apt-get update",
            normalized="apt-get update",
            timestamp=1.0,
        ),
        Command(
            session_id=session_id,
            raw="apt-get update",  # Duplicate
            normalized="apt-get update",
            timestamp=2.0,
        ),
        Command(
            session_id=session_id,
            raw="apt-get update",  # Duplicate
            normalized="apt-get update",
            timestamp=3.0,
        ),
        Command(
            session_id=session_id,
            raw="systemctl start nginx",
            normalized="systemctl start nginx",
            timestamp=4.0,
        ),
        Command(
            session_id=session_id,
            raw="systemctl start nginx",  # Duplicate
            normalized="systemctl start nginx",
            timestamp=5.0,
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify most common commands
    assert len(report.most_common_commands) <= 5
    # Should have "apt-get update" with count 3
    command_counts = dict(report.most_common_commands)
    assert command_counts["apt-get update"] == 3
    assert command_counts["systemctl start nginx"] == 2


def test_compile_report_includes_sudo_count(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report includes sudo command count."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create mix of sudo and non-sudo commands
    commands = [
        Command(
            session_id=session_id,
            raw="sudo apt-get install nginx",
            normalized="apt-get install nginx",
            sudo=True,
            timestamp=1.0,
        ),
        Command(
            session_id=session_id,
            raw="sudo systemctl start nginx",
            normalized="systemctl start nginx",
            sudo=True,
            timestamp=2.0,
        ),
        Command(
            session_id=session_id,
            raw="ls -la",  # No sudo
            normalized="ls -la",
            sudo=False,
            timestamp=3.0,
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify sudo count
    assert report.sudo_command_count == 2


def test_compile_report_handles_empty_commands(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report handles sessions with no commands gracefully."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Compile with no commands
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Verify report has zero values
    assert report.total_commands == 0
    assert report.high_confidence == 0
    assert report.medium_confidence == 0
    assert report.low_confidence == 0
    assert report.session_duration_seconds == 0.0
    assert report.sudo_command_count == 0
    assert len(report.module_breakdown) == 0
    assert len(report.most_common_commands) == 0


def test_compile_report_handles_commands_with_zero_timestamps(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    repo: SQLAlchemyRepository,
) -> None:
    """Test that report handles commands with zero timestamps."""
    from cli2ansible.application.dtos import SessionCreateRequestDTO

    # Create session
    req = SessionCreateRequestDTO(name="test-session", metadata={})
    session_dto = ingest_service.create_session(req)
    session_id = session_dto.id

    # Create commands with zero timestamps
    commands = [
        Command(
            session_id=session_id,
            raw="apt-get update",
            normalized="apt-get update",
            timestamp=0.0,  # Zero timestamp
        ),
        Command(
            session_id=session_id,
            raw="apt-get install nginx",
            normalized="apt-get install nginx",
            timestamp=0.0,  # Zero timestamp
        ),
    ]

    repo.save_commands(commands)

    # Compile and get report
    compile_service.compile(session_id)
    report = compile_service.get_report(session_id)

    # Duration should be 0 when all timestamps are 0
    assert report.session_duration_seconds == 0.0
    # But commands should still be processed
    assert report.total_commands == 2
