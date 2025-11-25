"""SQLAlchemy implementation of event repository."""

from typing import Any
from uuid import UUID

from cli2ansible.domain.entities import Event
from cli2ansible.domain.ports.repositories import EventRepositoryPort
from sqlalchemy import delete, select

from .db_helper import DatabaseHelper
from .sqlalchemy_orms import EventORM


class SQLAlchemyEventRepo(EventRepositoryPort):
    """SQLAlchemy implementation of event repository operations."""

    def __init__(self, engine: Any, session_local: Any) -> None:
        """Initialize with shared engine and SessionLocal."""
        self.engine = engine
        self.SessionLocal = session_local
        self.db_helper = DatabaseHelper(verbose=True)

    def save_events(self, events: list[Event]) -> None:
        """Save events for a session."""
        self.db_helper.log_transaction_start(f"Saving {len(events)} events")
        try:
            with self.SessionLocal() as db:
                self.db_helper.log_query("INSERT", "events", f"count={len(events)}")
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
                self.db_helper.log_transaction_commit(f"Saved {len(events)} events")
                self.db_helper.log_success("Events saved", len(events))
        except Exception as e:
            self.db_helper.log_error("save events", e)
            raise

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

    def delete_events(self, session_id: UUID) -> None:
        """Delete all events for a session."""
        with self.SessionLocal() as db:
            db.execute(delete(EventORM).where(EventORM.session_id == str(session_id)))
            db.commit()

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
