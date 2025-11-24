"""Port for parsing terminal recordings."""

from abc import ABC, abstractmethod

from cli2ansible.domain.entities import Event


class CapturePort(ABC):
    """Port for parsing terminal recordings."""

    @abstractmethod
    def parse_events(self, recording_data: bytes) -> list[Event]:
        """Parse recording into events."""
        ...
