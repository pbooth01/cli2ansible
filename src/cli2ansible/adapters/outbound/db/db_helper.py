"""Database helper utility for common database operations.

This utility provides common functionality used across repository classes
for logging, error handling, and connection management.
"""

import sys
from typing import Any


class DatabaseHelper:
    """Helper class for database operations with logging and error handling."""

    def __init__(self, verbose: bool = True):
        """Initialize database helper.

        Args:
            verbose: Whether to print verbose operation logs
        """
        self.verbose = verbose

    def log_query(self, operation: str, table: str, details: str = "") -> None:
        """Log a database query operation.

        Args:
            operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
            table: Table name being queried
            details: Additional details about the query
        """
        if self.verbose:
            message = f"[DB] {operation} on {table}"
            if details:
                message += f" - {details}"
            print(message)

    def log_error(self, operation: str, error: Exception) -> None:
        """Log a database error.

        Args:
            operation: Operation that failed
            error: Exception that occurred
        """
        print(f"[DB ERROR] {operation} failed: {str(error)}", file=sys.stderr)

    def log_success(self, operation: str, count: int = 0) -> None:
        """Log a successful database operation.

        Args:
            operation: Operation that succeeded
            count: Number of records affected (if applicable)
        """
        if self.verbose:
            message = f"[DB SUCCESS] {operation}"
            if count > 0:
                message += f" ({count} records)"
            print(message)

    def log_connection(self, status: str) -> None:
        """Log database connection status.

        Args:
            status: Connection status message
        """
        if self.verbose:
            print(f"[DB CONNECTION] {status}")

    def validate_session(self, session: Any) -> bool:
        """Validate that a database session is active.

        Args:
            session: Database session to validate

        Returns:
            True if session is valid, False otherwise
        """
        if session is None:
            print("[DB WARNING] Attempted operation with null session", file=sys.stderr)
            return False
        return True

    def log_transaction_start(self, operation: str) -> None:
        """Log the start of a database transaction.

        Args:
            operation: Description of the transaction
        """
        if self.verbose:
            print(f"[DB TRANSACTION] Starting: {operation}")

    def log_transaction_commit(self, operation: str) -> None:
        """Log a successful transaction commit.

        Args:
            operation: Description of the transaction
        """
        if self.verbose:
            print(f"[DB TRANSACTION] Committed: {operation}")

    def log_transaction_rollback(self, operation: str, reason: str = "") -> None:
        """Log a transaction rollback.

        Args:
            operation: Description of the transaction
            reason: Reason for rollback
        """
        message = f"[DB TRANSACTION] Rolled back: {operation}"
        if reason:
            message += f" - Reason: {reason}"
        print(message, file=sys.stderr)

