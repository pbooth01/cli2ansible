"""Port for translating commands to Ansible tasks."""

from abc import ABC, abstractmethod

from cli2ansible.domain.entities import Command, Task


class TranslatorPort(ABC):
    """Port for translating commands to Ansible tasks."""

    @abstractmethod
    def translate(self, command: Command) -> Task | None:
        """Translate a command to an Ansible task."""
        ...
