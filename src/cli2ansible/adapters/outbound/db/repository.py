"""SQLAlchemy repository implementation."""

from uuid import UUID

from cli2ansible.domain.models import CastFile, Command, Event, SessionStatus
from cli2ansible.domain.models import Session as DomainSession
from cli2ansible.domain.ports import SessionRepositoryPort
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .orm import Base, CastFileORM, CommandORM, EventORM, SessionORM


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

    def create_tables(self) -> None:
        """Create database tables."""
        Base.metadata.create_all(self.engine)

    def create(self, session: DomainSession) -> DomainSession:
        """Create a new session."""
        with self.SessionLocal() as db:
            orm_session = SessionORM(
                id=str(session.id),
                name=session.name,
                status=session.status.value,
                session_metadata=session.metadata,
            )
            db.add(orm_session)
            db.commit()
            db.refresh(orm_session)
            return self._to_domain(orm_session)

    def get(self, session_id: UUID) -> DomainSession | None:
        """Retrieve a session by ID."""
        with self.SessionLocal() as db:
            stmt = select(SessionORM).where(SessionORM.id == str(session_id))
            orm_session = db.scalar(stmt)
            return self._to_domain(orm_session) if orm_session else None

    def list_all(self) -> list[DomainSession]:
        """List all sessions."""
        with self.SessionLocal() as db:
            stmt = select(SessionORM).order_by(SessionORM.created_at.desc())
            orm_sessions = db.scalars(stmt).all()
            return [self._to_domain(s) for s in orm_sessions]

    def update(self, session: DomainSession) -> DomainSession:
        """Update session."""
        with self.SessionLocal() as db:
            stmt = select(SessionORM).where(SessionORM.id == str(session.id))
            orm_session = db.scalar(stmt)
            if not orm_session:
                raise ValueError(f"Session {session.id} not found")

            orm_session.name = session.name
            orm_session.status = session.status.value
            orm_session.session_metadata = session.metadata
            db.commit()
            db.refresh(orm_session)
            return self._to_domain(orm_session)

    def delete(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        with self.SessionLocal() as db:
            # Delete related cast files
            db.execute(delete(CastFileORM).where(CastFileORM.session_id == str(session_id)))
            # Delete related commands
            db.execute(delete(CommandORM).where(CommandORM.session_id == str(session_id)))
            # Delete related events
            db.execute(delete(EventORM).where(EventORM.session_id == str(session_id)))
            # Delete the session
            db.execute(delete(SessionORM).where(SessionORM.id == str(session_id)))
            db.commit()

    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        with self.SessionLocal() as db:
            orm_events = [
                EventORM(
                    id=str(event.id),
                    session_id=str(event.session_id),
                    timestamp=event.timestamp,
                    event_type=event.event_type,
                    data=event.data,
                    sequence=event.sequence,
                    version=event.version,
                )
                for event in events
            ]
            db.add_all(orm_events)
            db.commit()

    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        with self.SessionLocal() as db:
            stmt = (
                select(EventORM)
                .where(EventORM.session_id == str(session_id))
                .order_by(EventORM.sequence)
            )
            orm_events = db.scalars(stmt).all()
            return [self._event_to_domain(e) for e in orm_events]

    def save_commands(self, commands: list[Command]) -> None:
        """Save parsed commands."""
        with self.SessionLocal() as db:
            orm_commands = [
                CommandORM(
                    session_id=str(cmd.session_id),
                    raw=cmd.raw,
                    normalized=cmd.normalized,
                    cwd=cmd.cwd,
                    user=cmd.user,
                    sudo=cmd.sudo,
                    timestamp=cmd.timestamp,
                    exit_code=cmd.exit_code,
                    output=cmd.output,
                )
                for cmd in commands
            ]
            db.add_all(orm_commands)
            db.commit()

    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        with self.SessionLocal() as db:
            stmt = (
                select(CommandORM)
                .where(CommandORM.session_id == str(session_id))
                .order_by(CommandORM.event_sequence, CommandORM.timestamp, CommandORM.id)
            )
            orm_commands = db.scalars(stmt).all()
            return [self._command_to_domain(c) for c in orm_commands]

    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        with self.SessionLocal() as db:
            db.execute(delete(EventORM).where(EventORM.session_id == str(session_id)))
            db.commit()

    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        with self.SessionLocal() as db:
            db.execute(delete(CommandORM).where(CommandORM.session_id == str(session_id)))
            db.commit()

    def _to_domain(self, orm_session: SessionORM) -> DomainSession:
        """Convert ORM to domain model."""
        return DomainSession(
            id=UUID(orm_session.id),
            name=orm_session.name,
            status=SessionStatus(orm_session.status),
            created_at=orm_session.created_at,
            updated_at=orm_session.updated_at,
            metadata=orm_session.session_metadata,
        )

    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        with self.SessionLocal() as db:
            stmt = select(EventORM).where(EventORM.id == str(event_id))
            orm_event = db.scalar(stmt)
            return self._event_to_domain(orm_event) if orm_event else None

    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        with self.SessionLocal() as db:
            stmt = select(EventORM).where(EventORM.id == str(event.id))
            orm_event = db.scalar(stmt)
            if not orm_event:
                raise ValueError(f"Event {event.id} not found")

            orm_event.timestamp = event.timestamp
            orm_event.event_type = event.event_type
            orm_event.data = event.data
            orm_event.sequence = event.sequence
            orm_event.version = event.version
            db.commit()
            db.refresh(orm_event)
            return self._event_to_domain(orm_event)

    def _event_to_domain(self, orm_event: EventORM) -> Event:
        """Convert ORM event to domain model."""
        return Event(
            id=UUID(orm_event.id),
            session_id=UUID(orm_event.session_id),
            timestamp=orm_event.timestamp,
            event_type=orm_event.event_type,
            data=orm_event.data,
            sequence=orm_event.sequence,
            version=orm_event.version,
        )

    def _command_to_domain(self, orm_cmd: CommandORM) -> Command:
        """Convert ORM command to domain model."""
        return Command(
            session_id=UUID(orm_cmd.session_id),
            raw=orm_cmd.raw,
            normalized=orm_cmd.normalized,
            cwd=orm_cmd.cwd,
            user=orm_cmd.user,
            sudo=orm_cmd.sudo,
            timestamp=orm_cmd.timestamp,
            exit_code=orm_cmd.exit_code,
            output=orm_cmd.output,
            event_sequence=orm_cmd.event_sequence,
        )

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
