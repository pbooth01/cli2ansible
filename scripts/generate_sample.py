#!/usr/bin/env python3
"""Generate a sample Ansible role for testing."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli2ansible.adapters.outbound.generators.ansible_role import AnsibleRoleGenerator
from cli2ansible.domain.models import Role, Task, TaskConfidence


def main() -> None:
    """Generate sample role."""
    # Create sample tasks
    tasks = [
        Task(
            name="Update apt cache",
            module="apt",
            args={"update_cache": True, "cache_valid_time": 3600},
            confidence=TaskConfidence.HIGH,
            become=True,
        ),
        Task(
            name="Install nginx",
            module="apt",
            args={"name": "nginx", "state": "present"},
            confidence=TaskConfidence.HIGH,
            become=True,
        ),
        Task(
            name="Start and enable nginx",
            module="systemd",
            args={"name": "nginx", "state": "started", "enabled": True},
            confidence=TaskConfidence.HIGH,
            become=True,
        ),
    ]

    # Create role
    role = Role(
        name="sample_role",
        tasks=tasks,
        vars={"nginx_port": 80},
        defaults={"nginx_worker_processes": 4},
    )

    # Generate
    output_path = Path(__file__).parent.parent / "artifacts" / "sample_role"
    generator = AnsibleRoleGenerator()
    generator.generate(role, str(output_path))

    print(f"✅ Generated sample role at: {output_path}")
    print("\nTo test with ansible-lint:")
    print(f"  ansible-lint {output_path}")


if __name__ == "__main__":
    main()
