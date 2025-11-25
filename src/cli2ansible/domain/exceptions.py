"""Domain layer exceptions."""


class DomainError(Exception):
    """Base exception for domain layer errors."""

    pass


class SessionNotFoundError(DomainError):
    """Raised when a session cannot be found."""

    pass


class EventNotFoundError(DomainError):
    """Raised when an event cannot be found."""

    pass


class VersionConflictError(DomainError):
    """Raised when an event update has a version conflict."""

    pass


class InvalidSessionStateError(DomainError):
    """Raised when an operation is invalid for the current session state."""

    pass


class InvalidEventStateError(DomainError):
    """Raised when an operation is invalid for the current event state."""

    pass


class InvalidFileError(DomainError):
    """Raised when a file is invalid or cannot be processed."""

    pass


class ObjectNotFoundError(DomainError):
    """Raised when an object is not found in storage."""

    pass


class ObjectStoreError(DomainError):
    """Raised when object store operations fail."""

    pass
