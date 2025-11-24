"""Application layer errors with HTTP semantics."""

from typing import Any


class ApplicationError(Exception):
    """Base exception for application layer errors."""

    code: str = "application_error"
    status: int = 500

    def __init__(self, message: str = "", details: dict[str, Any] | None = None):
        """Initialize application error.

        Args:
            message: Human-readable error message.
            details: Optional structured error details for clients.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return error message."""
        return self.message


class BadRequestError(ApplicationError):
    """Raised when request input is invalid (400)."""

    code = "bad_request"
    status = 400


class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found (404)."""

    code = "not_found"
    status = 404


class ConflictError(ApplicationError):
    """Raised on state conflicts (409) - e.g., version conflicts."""

    code = "conflict"
    status = 409


class UnprocessableEntityError(ApplicationError):
    """Raised when request is well-formed but semantically invalid (422)."""

    code = "unprocessable_entity"
    status = 422


class TooLargeError(ApplicationError):
    """Raised when request payload is too large (413)."""

    code = "payload_too_large"
    status = 413


class DependencyFailedError(ApplicationError):
    """Raised when external dependency fails (424 or 502/503 depending on policy)."""

    code = "dependency_failed"
    status = 424


class ServiceUnavailableError(ApplicationError):
    """Raised when service is unavailable (503)."""

    code = "service_unavailable"
    status = 503
