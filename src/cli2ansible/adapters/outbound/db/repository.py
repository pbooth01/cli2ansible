"""SQLAlchemy repository implementation."""

from uuid import UUID

from cli2ansible.domain.entities import CastFile, Command, Event
from cli2ansible.domain.entities import Session as DomainSession
from cli2ansible.domain.ports import SessionRepositoryPort
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .sqlalchemy_command_repo import SQLAlchemyCommandRepo
from .sqlalchemy_event_repo import SQLAlchemyEventRepo
from .sqlalchemy_orms import Base, CastFileORM
from .sqlalchemy_session_repo import SQLAlchemySessionRepo


class SQLAlchemyRepository(SessionRepositoryPort):
    """SQLAlchemy implementation of session repository."""

    def __init__(self, database_url: str) -> None:
        # For SQLite in-memory databases, use StaticPool to share the same connection
        # across all sessions, allowing tables to persist
        connect_args = {}
        poolclass = None
        if database_url.startswith("sqlite") and ":memory:" in database_url:
            # Use shared cache for in-memory SQLite to allow connection sharing
            if "cache=shared" not in database_url:
                database_url = database_url.replace(":memory:", ":memory:?cache=shared")
            connect_args = {"check_same_thread": False}
            poolclass = StaticPool

        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            poolclass=poolclass,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Initialize specialized repositories
        self.session_repo = SQLAlchemySessionRepo(self.engine, self.SessionLocal)
        self.event_repo = SQLAlchemyEventRepo(self.engine, self.SessionLocal)
        self.command_repo = SQLAlchemyCommandRepo(self.engine, self.SessionLocal)

    def create_tables(self) -> None:
        """Create database tables."""
        Base.metadata.create_all(self.engine)

    def create(self, session: DomainSession) -> DomainSession:
        """Create a new session."""
        return self.session_repo.create(session)

    def get(self, session_id: UUID) -> DomainSession | None:
        """Retrieve a session by ID."""
        return self.session_repo.get(session_id)

    def list_all(self, tags: list[str] | None = None) -> list[DomainSession]:
        """List all sessions, optionally filtered by tags."""
        return self.session_repo.list_all(tags=tags)

    def update(self, session: DomainSession) -> DomainSession:
        """Update session."""
        return self.session_repo.update(session)

    def delete(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        return self.session_repo.delete(session_id)

    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        return self.event_repo.save_events(events)

    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        return self.event_repo.get_events(session_id)

    def save_commands(self, commands: list[Command]) -> None:
        """Save parsed commands."""
        return self.command_repo.save_commands(commands)

    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        return self.command_repo.get_commands(session_id)

    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        return self.event_repo.delete_events(session_id)

    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        return self.command_repo.delete_commands(session_id)

    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        return self.event_repo.get_event_by_id(event_id)

    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        return self.event_repo.update_event(event)

    def save_cast_file(self, cast_file: CastFile) -> CastFile:
        """Save a cast file record."""
        with self.SessionLocal() as db:
            orm_cast_file = CastFileORM(
                id=str(cast_file.id),
                session_id=str(cast_file.session_id),
                file_name=cast_file.file_name,
                file_size=cast_file.file_size,
            )
            db.add(orm_cast_file)
            db.commit()
            db.refresh(orm_cast_file)
            return self._cast_file_to_domain(orm_cast_file)

    def get_cast_file(self, session_id: UUID) -> CastFile | None:
        """Get the most recent cast file for a session."""
        with self.SessionLocal() as db:
            stmt = (
                select(CastFileORM)
                .where(CastFileORM.session_id == str(session_id))
                .order_by(CastFileORM.uploaded_at.desc())
                .limit(1)
            )
            orm_cast_file = db.scalar(stmt)
            return self._cast_file_to_domain(orm_cast_file) if orm_cast_file else None

    def _cast_file_to_domain(self, orm_cast_file: CastFileORM) -> CastFile:
        """Convert ORM cast file to domain model."""
        return CastFile(
            id=UUID(orm_cast_file.id),
            session_id=UUID(orm_cast_file.session_id),
            file_name=orm_cast_file.file_name,
            file_size=orm_cast_file.file_size,
            uploaded_at=orm_cast_file.uploaded_at,
        )
