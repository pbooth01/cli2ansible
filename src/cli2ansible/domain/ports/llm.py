"""Port for LLM-based command analysis and cleaning."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.domain.entities import CleanedCommand, CleaningReport, Command


class LLMPort(ABC):
    """Port for LLM-based command analysis and cleaning."""

    @abstractmethod
    def clean_commands(
        self, commands: list[Command], session_id: UUID
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """
        Analyze terminal commands and remove duplicates and error corrections.

        Returns a tuple of (cleaned_commands, cleaning_report).
        """
        ...
