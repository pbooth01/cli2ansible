#!/usr/bin/env python3
"""
Docker Development Environment Manager

Manages Docker Compose services for cli2ansible development.

Usage:
    python3 docker.py <command> [OPTIONS]
"""

import argparse
import subprocess


def get_compose_cmd():
    """Determine the correct docker compose command."""
    result = subprocess.run(
        ["docker", "compose", "version"], capture_output=True, check=False
    )
    if result.returncode == 0:
        return ["docker", "compose"]
    return ["docker-compose"]


def run_compose(args, follow=False):
    """Run docker compose command."""
    cmd = get_compose_cmd() + args
    print(f"→ Running: {' '.join(cmd)}\n")

    if follow:
        # For logs -f, we need to stream output
        try:
            subprocess.run(cmd, check=False)
        except KeyboardInterrupt:
            print("\n\nStopped following logs.")
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0


def cmd_up(services):
    """Start services."""
    print("🚀 Starting Docker services...\n")
    args = ["up", "-d"]
    if services:
        args.extend(services)
    success = run_compose(args)
    if success:
        print("\n✅ Services started!")
        print("\n📍 Access URLs:")
        print("   API:         http://localhost:8000")
        print("   API Docs:    http://localhost:8000/docs")
        print("   Frontend:    http://localhost:3000")
        print("   MinIO:       http://localhost:9001")


def cmd_down(services):
    """Stop services."""
    print("🛑 Stopping Docker services...\n")
    args = ["down"]
    run_compose(args)
    print("\n✅ Services stopped!")


def cmd_restart(services):
    """Restart services."""
    print("🔄 Restarting Docker services...\n")
    args = ["restart"]
    if services:
        args.extend(services)
    run_compose(args)
    print("\n✅ Services restarted!")


def cmd_logs(services, follow, tail):
    """View service logs."""
    print("📋 Viewing logs...\n")
    args = ["logs"]
    if tail:
        args.extend(["--tail", str(tail)])
    if follow:
        args.append("-f")
    if services:
        args.extend(services)
    run_compose(args, follow=follow)


def cmd_status(services):
    """Show service status."""
    print("📊 Service Status\n")
    run_compose(["ps"])


def cmd_clean(services):
    """Stop services and remove volumes."""
    print("🧹 Cleaning Docker environment...\n")
    print("⚠️  This will remove all data (database, uploaded files)!\n")
    run_compose(["down", "-v"])
    print("\n✅ Environment cleaned!")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Docker development services for cli2ansible"
    )
    parser.add_argument(
        "command",
        choices=["up", "down", "restart", "logs", "status", "clean"],
        help="Command to run",
    )
    parser.add_argument(
        "--service",
        "-s",
        action="append",
        dest="services",
        choices=["postgres", "minio", "app", "web"],
        help="Target specific service(s)",
    )
    parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
    parser.add_argument("--tail", type=int, default=100, help="Number of log lines")

    args = parser.parse_args()
    services = args.services or []

    commands = {
        "up": lambda: cmd_up(services),
        "down": lambda: cmd_down(services),
        "restart": lambda: cmd_restart(services),
        "logs": lambda: cmd_logs(services, args.follow, args.tail),
        "status": lambda: cmd_status(services),
        "clean": lambda: cmd_clean(services),
    }

    commands[args.command]()


if __name__ == "__main__":
    main()
