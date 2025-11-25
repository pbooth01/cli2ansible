"""Input port for playbook compilation use case."""

from abc import ABC, abstractmethod
from uuid import UUID

from cli2ansible.application.dtos import CompileResponseDTO
from cli2ansible.domain.entities import Report


class CompilePlaybookUseCase(ABC):
    """Use case for compiling sessions to Ansible playbooks."""

    @abstractmethod
    def compile(self, session_id: UUID) -> CompileResponseDTO:
        """Compile session to Ansible playbook."""
        ...

    @abstractmethod
    def get_report(self, session_id: UUID) -> Report:
        """Get translation report for a session."""
        ...
