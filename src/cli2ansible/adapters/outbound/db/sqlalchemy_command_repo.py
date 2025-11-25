"""SQLAlchemy implementation of command repository."""

from typing import Any
from uuid import UUID

from cli2ansible.domain.entities import Command
from cli2ansible.domain.ports.repositories import CommandRepositoryPort
from sqlalchemy import delete, select

from .sqlalchemy_orms import CommandORM


class SQLAlchemyCommandRepo(CommandRepositoryPort):
    """SQLAlchemy implementation of command repository operations."""

    def __init__(self, engine: Any, session_local: Any) -> None:
        """Initialize with shared engine and SessionLocal."""
        self.engine = engine
        self.SessionLocal = session_local

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
                .order_by(
                    CommandORM.event_sequence, CommandORM.timestamp, CommandORM.id
                )
            )
            orm_commands = db.scalars(stmt).all()
            return [self._command_to_domain(c) for c in orm_commands]

    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        with self.SessionLocal() as db:
            db.execute(
                delete(CommandORM).where(CommandORM.session_id == str(session_id))
            )
            db.commit()

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
