"""Ports for artifact storage and role generation."""

from abc import ABC, abstractmethod

from cli2ansible.domain.entities import Role


class ObjectStorePort(ABC):
    """Port for artifact storage."""

    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload artifact and return URL."""
        ...

    @abstractmethod
    def download(self, key: str) -> bytes:
        """Download artifact."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete artifact."""
        ...

    @abstractmethod
    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL."""
        ...


class RoleGeneratorPort(ABC):
    """Port for generating Ansible role artifacts."""

    @abstractmethod
    def generate(self, role: Role, output_path: str) -> None:
        """Generate role directory structure."""
        ...
