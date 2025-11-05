"""Rule-based command to Ansible task translator."""

import re
from typing import Any

from cli2ansible.domain.models import Command, Task, TaskConfidence
from cli2ansible.domain.ports import TranslatorPort


class RulesEngine(TranslatorPort):
    """Translates shell commands to Ansible tasks using rules."""

    def __init__(self) -> None:
        self.rules = [
            self._apt_install,
            self._yum_install,
            self._dnf_install,
            self._systemctl,
            self._mkdir,
            self._copy_file,
            self._git_clone,
            self._pip_install,
            self._npm_install,
            self._useradd,
            self._chown,
            self._chmod,
        ]

    def translate(self, command: Command) -> Task | None:
        """Translate a command to an Ansible task."""
        cmd = command.normalized.strip()

        # Skip empty commands
        if not cmd:
            return None

        # Try each rule
        for rule in self.rules:
            task = rule(command)
            if task:
                return task

        # Fallback to shell module
        return Task(
            name=f"Run: {cmd[:50]}",
            module="shell",
            args={"cmd": cmd},
            confidence=TaskConfidence.LOW,
            original_command=cmd,
            become=command.sudo,
        )

    def _apt_install(self, command: Command) -> Task | None:
        """Translate apt install commands."""
        match = re.match(r"apt(?:-get)?\s+install\s+(?:-y\s+)?(.+)", command.normalized)
        if match:
            packages = match.group(1).strip().split()
            return Task(
                name=f"Install packages: {', '.join(packages)}",
                module="apt",
                args={"name": packages, "state": "present", "update_cache": True},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _yum_install(self, command: Command) -> Task | None:
        """Translate yum install commands."""
        match = re.match(r"yum\s+install\s+(?:-y\s+)?(.+)", command.normalized)
        if match:
            packages = match.group(1).strip().split()
            return Task(
                name=f"Install packages: {', '.join(packages)}",
                module="yum",
                args={"name": packages, "state": "present"},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _dnf_install(self, command: Command) -> Task | None:
        """Translate dnf install commands."""
        match = re.match(r"dnf\s+install\s+(?:-y\s+)?(.+)", command.normalized)
        if match:
            packages = match.group(1).strip().split()
            return Task(
                name=f"Install packages: {', '.join(packages)}",
                module="dnf",
                args={"name": packages, "state": "present"},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _systemctl(self, command: Command) -> Task | None:
        """Translate systemctl commands."""
        match = re.match(
            r"systemctl\s+(start|stop|restart|enable|disable)\s+(\S+)",
            command.normalized,
        )
        if match:
            action, service = match.groups()
            state_map = {"start": "started", "stop": "stopped", "restart": "restarted"}
            if action in state_map:
                return Task(
                    name=f"{action.capitalize()} service: {service}",
                    module="systemd",
                    args={"name": service, "state": state_map[action]},
                    confidence=TaskConfidence.HIGH,
                    original_command=command.raw,
                    become=command.sudo,
                )
            elif action in ["enable", "disable"]:
                return Task(
                    name=f"{action.capitalize()} service: {service}",
                    module="systemd",
                    args={"name": service, "enabled": action == "enable"},
                    confidence=TaskConfidence.HIGH,
                    original_command=command.raw,
                    become=command.sudo,
                )
        return None

    def _mkdir(self, command: Command) -> Task | None:
        """Translate mkdir commands."""
        match = re.match(r"mkdir\s+(?:-p\s+)?(.+)", command.normalized)
        if match:
            path = match.group(1).strip()
            return Task(
                name=f"Create directory: {path}",
                module="file",
                args={"path": path, "state": "directory"},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
                creates=path,
            )
        return None

    def _copy_file(self, command: Command) -> Task | None:
        """Translate cp commands."""
        match = re.match(r"cp\s+(?:-r\s+)?(\S+)\s+(\S+)", command.normalized)
        if match:
            src, dest = match.groups()
            return Task(
                name=f"Copy {src} to {dest}",
                module="copy",
                args={"src": src, "dest": dest},
                confidence=TaskConfidence.MEDIUM,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _git_clone(self, command: Command) -> Task | None:
        """Translate git clone commands."""
        match = re.match(r"git\s+clone\s+(\S+)(?:\s+(\S+))?", command.normalized)
        if match:
            repo = match.group(1)
            dest = match.group(2) or repo.split("/")[-1].replace(".git", "")
            return Task(
                name=f"Clone repository: {repo}",
                module="git",
                args={"repo": repo, "dest": dest},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                creates=dest,
            )
        return None

    def _pip_install(self, command: Command) -> Task | None:
        """Translate pip install commands."""
        match = re.match(r"pip[3]?\s+install\s+(.+)", command.normalized)
        if match:
            packages = match.group(1).strip().split()
            return Task(
                name=f"Install Python packages: {', '.join(packages)}",
                module="pip",
                args={"name": packages, "state": "present"},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
            )
        return None

    def _npm_install(self, command: Command) -> Task | None:
        """Translate npm install commands."""
        match = re.match(r"npm\s+install\s+(?:-g\s+)?(.+)", command.normalized)
        if match:
            packages = match.group(1).strip().split()
            is_global = "-g" in command.normalized
            return Task(
                name=f"Install npm packages: {', '.join(packages)}",
                module="npm",
                args={"name": ", ".join(packages), "global": is_global},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
            )
        return None

    def _useradd(self, command: Command) -> Task | None:
        """Translate useradd commands."""
        match = re.match(r"useradd\s+(?:-m\s+)?(\S+)", command.normalized)
        if match:
            username = match.group(1)
            return Task(
                name=f"Create user: {username}",
                module="user",
                args={"name": username, "state": "present", "create_home": True},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _chown(self, command: Command) -> Task | None:
        """Translate chown commands."""
        match = re.match(r"chown\s+(?:-R\s+)?(\S+)\s+(.+)", command.normalized)
        if match:
            owner, path = match.groups()
            args: dict[str, Any] = {"path": path}
            if ":" in owner:
                user, group = owner.split(":")
                args["owner"] = user
                args["group"] = group
            else:
                args["owner"] = owner
            return Task(
                name=f"Change ownership of {path}",
                module="file",
                args=args,
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None

    def _chmod(self, command: Command) -> Task | None:
        """Translate chmod commands."""
        match = re.match(r"chmod\s+(?:-R\s+)?(\S+)\s+(.+)", command.normalized)
        if match:
            mode, path = match.groups()
            return Task(
                name=f"Change permissions of {path}",
                module="file",
                args={"path": path, "mode": mode},
                confidence=TaskConfidence.HIGH,
                original_command=command.raw,
                become=command.sudo,
            )
        return None
