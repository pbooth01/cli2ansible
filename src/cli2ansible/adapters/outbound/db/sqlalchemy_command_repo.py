"""SQLAlchemy implementation of command repository."""

import sys
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
        print(f"[DB TRANSACTION] Starting: Saving {len(commands)} commands")
        try:
            with self.SessionLocal() as db:
                print(f"[DB] INSERT on commands - count={len(commands)}")
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
                print(f"[DB TRANSACTION] Committed: Saved {len(commands)} commands")
                print(f"[DB SUCCESS] Commands saved ({len(commands)} records)")
        except Exception as e:
            print(f"[DB ERROR] save commands failed: {str(e)}", file=sys.stderr)
            raise

    def get_commands(self, session_id: UUID) -> list[Command]:
        """Get all commands for a session."""
        print(f"[DB] SELECT on commands - session_id={session_id}")
        try:
            with self.SessionLocal() as db:
                stmt = (
                    select(CommandORM)
                    .where(CommandORM.session_id == str(session_id))
                    .order_by(CommandORM.event_sequence, CommandORM.timestamp, CommandORM.id)
                )
                orm_commands = db.scalars(stmt).all()
                result = [self._command_to_domain(c) for c in orm_commands]
                print(f"[DB SUCCESS] Commands retrieved ({len(result)} records)")
                return result
        except Exception as e:
            print(f"[DB ERROR] get commands failed: {str(e)}", file=sys.stderr)
            raise

    def delete_commands(self, session_id: UUID) -> None:
        """Delete all commands for a session."""
        with self.SessionLocal() as db:
            db.execute(delete(CommandORM).where(CommandORM.session_id == str(session_id)))
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
