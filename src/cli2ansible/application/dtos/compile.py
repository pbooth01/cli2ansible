"""Compilation-related DTOs."""

from dataclasses import dataclass


@dataclass
class CompileRequestDTO:
    """Request to compile a session to Ansible playbook."""

    pass  # No specific fields needed, session_id comes from URL


@dataclass
class CompileResponseDTO:
    """Response from compilation."""

    artifact_url: str
    download_url: str
