"""SQLAlchemy implementation of session repository."""

import sys
from typing import Any
from uuid import UUID

from cli2ansible.domain.entities import Command, Event, SessionStatus
from cli2ansible.domain.entities import Session as DomainSession
from cli2ansible.domain.ports.repositories import SessionRepositoryPort
from sqlalchemy import delete, select

from .sqlalchemy_orms import CastFileORM, CommandORM, EventORM, SessionORM


class SQLAlchemySessionRepo(SessionRepositoryPort):
    """SQLAlchemy implementation of session repository operations."""

    def __init__(self, engine: Any, session_local: Any) -> None:
        """Initialize with shared engine and SessionLocal."""
        self.engine = engine
        self.SessionLocal = session_local

    def create(self, session: DomainSession) -> DomainSession:
        """Create a new session."""
        print(f"[DB TRANSACTION] Starting: Creating session {session.id}")
        try:
            with self.SessionLocal() as db:
                if db is None:
                    print("[DB WARNING] Attempted operation with null session", file=sys.stderr)
                    raise ValueError("Invalid database session")

                print(f"[DB] INSERT on sessions - id={session.id}")
                orm_session = SessionORM(
                    id=str(session.id),
                    name=session.name,
                    status=session.status.value,
                    session_metadata=session.metadata,
                )
                db.add(orm_session)
                db.commit()
                db.refresh(orm_session)
                print(f"[DB TRANSACTION] Committed: Created session {session.id}")
                print(f"[DB SUCCESS] Session created (1 records)")
                return self._to_domain(orm_session)
        except Exception as e:
            print(f"[DB ERROR] create session failed: {str(e)}", file=sys.stderr)
            raise

    def get(self, session_id: UUID) -> DomainSession | None:
        """Retrieve a session by ID."""
        print(f"[DB] SELECT on sessions - id={session_id}")
        try:
            with self.SessionLocal() as db:
                stmt = select(SessionORM).where(SessionORM.id == str(session_id))
                orm_session = db.scalar(stmt)
                if orm_session:
                    print(f"[DB SUCCESS] Session retrieved (1 records)")
                return self._to_domain(orm_session) if orm_session else None
        except Exception as e:
            print(f"[DB ERROR] get session failed: {str(e)}", file=sys.stderr)
            raise

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
        print(f"[DB TRANSACTION] Starting: Deleting session {session_id} and related data")
        try:
            with self.SessionLocal() as db:
                # Delete related cast files
                print(f"[DB] DELETE on cast_files - session_id={session_id}")
                db.execute(delete(CastFileORM).where(CastFileORM.session_id == str(session_id)))
                # Delete related commands
                print(f"[DB] DELETE on commands - session_id={session_id}")
                db.execute(delete(CommandORM).where(CommandORM.session_id == str(session_id)))
                # Delete related events
                print(f"[DB] DELETE on events - session_id={session_id}")
                db.execute(delete(EventORM).where(EventORM.session_id == str(session_id)))
                # Delete the session
                print(f"[DB] DELETE on sessions - id={session_id}")
                db.execute(delete(SessionORM).where(SessionORM.id == str(session_id)))
                db.commit()
                print(f"[DB TRANSACTION] Committed: Deleted session {session_id}")
                print(f"[DB SUCCESS] Session and related data deleted")
        except Exception as e:
            print(f"[DB ERROR] delete session failed: {str(e)}", file=sys.stderr)
            raise

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

    # Event operations - not implemented in this repository
    # These are delegated to EventRepositoryPort in the facade
    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        raise NotImplementedError("Use EventRepositoryPort directly")

    def get_events(self, session_id: UUID) -> list[Event]:
        """Get all events for a session."""
        raise NotImplementedError("Use EventRepositoryPort directly")

    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        raise NotImplementedError("Use EventRepositoryPort directly")

    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        raise NotImplementedError("Use EventRepositoryPort directly")

    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        raise NotImplementedError("Use EventRepositoryPort directly")

    # Command operations - not implemented in this repository
    # These are delegated to CommandRepositoryPort in the facade
    def save_commands(self, commands: list[Command]) -> None:
        """Save parsed commands."""
        raise NotImplementedError("Use CommandRepositoryPort directly")

    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        raise NotImplementedError("Use CommandRepositoryPort directly")

    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        raise NotImplementedError("Use CommandRepositoryPort directly")
