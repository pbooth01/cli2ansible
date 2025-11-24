"""Artifact building and export services."""

import tempfile
import zipfile
from pathlib import Path
from uuid import UUID

from cli2ansible.domain.entities import Role
from cli2ansible.domain.ports import ObjectStorePort, RoleGeneratorPort


class RoleArtifactExporter:
    """Service for building and exporting Ansible role artifacts."""

    def __init__(self, generator: RoleGeneratorPort, store: ObjectStorePort) -> None:
        """Initialize with role generator and object store ports."""
        self.generator = generator
        self.store = store

    def export(self, role: Role, session_id: UUID) -> str:
        """Generate and upload role artifact.

        Args:
            role: The Ansible role to export
            session_id: The session ID for artifact storage

        Returns:
            The artifact key/path in object storage
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            role_path = Path(tmpdir) / role.name
            role_path.mkdir()

            # Generate role files
            self.generator.generate(role, str(role_path))

            # Create zip archive
            zip_path = Path(tmpdir) / f"{role.name}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file in role_path.rglob("*"):
                    if file.is_file():
                        zipf.write(file, file.relative_to(role_path.parent))

            # Upload to object store
            with open(zip_path, "rb") as f:
                artifact_data = f.read()

            key = f"sessions/{session_id}/role.zip"
            result: str = self.store.upload(key, artifact_data, "application/zip")
            return result
