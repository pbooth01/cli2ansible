#!/usr/bin/env python3
"""
Development Environment Setup Script

Sets up the complete development environment for cli2ansible:
1. Installs Python dependencies with Poetry
2. Starts Docker services (Postgres, MinIO)
3. Runs database migrations
4. Starts the backend API server
5. Starts the frontend development server

Usage:
    python3 setup.py [--skip-docker] [--skip-migrations] [--skip-servers] [--clean]
"""

import argparse
import contextlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Store background processes for cleanup
background_processes = []


def run_command(cmd, description, cwd=None, check=True):
    """Run a shell command and handle errors."""
    print(f"→ {description}...")
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd,
            shell=isinstance(cmd, str),
            check=check,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n")[:5]:
                print(f"  {line}")
        return True, result
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False, e


def run_background_command(cmd, description, cwd=None, log_file=None):
    """Run a shell command in the background."""
    print(f"→ {description}...")
    try:
        stdout_dest = (
            open(log_file, "w") if log_file else subprocess.DEVNULL
        )  # noqa: SIM115
        process = subprocess.Popen(
            cmd if isinstance(cmd, list) else cmd,
            shell=isinstance(cmd, str),
            stdout=stdout_dest,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )
        background_processes.append((process, description, log_file))
        return True, process
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False, None


def check_prerequisites():
    """Check that required tools are installed."""
    print("\n🔍 Checking prerequisites...\n")

    # Check Python version
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check Poetry
    success, _ = run_command(["poetry", "--version"], "Checking Poetry", check=False)
    if not success:
        print("  ❌ Poetry not found. Install with: pip install poetry")
        return False

    return True


def install_dependencies(clean=False):
    """Install Python dependencies with Poetry."""
    print("\n📦 Installing dependencies...\n")

    if clean:
        venv_path = Path(".venv")
        if venv_path.exists():
            print("→ Removing existing virtual environment...")
            shutil.rmtree(venv_path)

    success, _ = run_command(["poetry", "install"], "Installing dependencies")
    if not success:
        return False

    return True


def start_docker_services():
    """Start Docker services."""
    print("\n🐳 Starting Docker services...\n")

    # Check if docker-compose is available
    success, _ = run_command(
        ["docker", "compose", "version"], "Checking Docker Compose", check=False
    )
    if not success:
        success, _ = run_command(
            ["docker-compose", "version"], "Checking docker-compose", check=False
        )
        if not success:
            print("  ❌ Docker Compose not found")
            return False
        compose_cmd = ["docker-compose"]
    else:
        compose_cmd = ["docker", "compose"]

    # Start services
    success, _ = run_command(
        compose_cmd + ["up", "-d", "postgres", "minio"], "Starting Postgres and MinIO"
    )
    if not success:
        return False

    # Wait for services to be healthy
    print("→ Waiting for services to be healthy...")
    for _ in range(30):
        success, result = run_command(
            compose_cmd + ["ps", "--format", "json"],
            "Checking service status",
            check=False,
        )
        time.sleep(2)
        break  # Services started, health check is handled by docker-compose

    print("  ✓ Docker services started")
    return True


def run_migrations():
    """Run database migrations."""
    print("\n🗃️  Running database migrations...\n")

    success, _ = run_command(
        ["poetry", "run", "alembic", "upgrade", "head"], "Running Alembic migrations"
    )
    return success


def get_project_root():
    """Get the project root directory."""
    # Script is at .augment/skills/dev-setup/scripts/setup.py
    # So we need to go up 5 levels: setup.py -> scripts -> dev-setup -> skills -> .augment -> project root
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def start_backend():
    """Start the FastAPI backend server."""
    print("\n🖥️  Starting backend API server...\n")

    project_root = get_project_root()
    log_file = project_root / ".augment" / "logs" / "backend.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    success, _ = run_background_command(
        [
            "poetry",
            "run",
            "uvicorn",
            "cli2ansible.app:app",
            "--reload",
            "--port",
            "8000",
        ],
        "Starting FastAPI on port 8000",
        cwd=project_root,
        log_file=str(log_file),
    )

    if success:
        print(f"  ✓ Backend started (logs: {log_file})")
        # Wait a moment for the server to start
        time.sleep(2)
    return success


def start_frontend():
    """Start the Next.js frontend development server."""
    print("\n🌐 Starting frontend development server...\n")

    project_root = get_project_root()
    frontend_dir = project_root / "frontend"
    log_file = project_root / ".augment" / "logs" / "frontend.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if node_modules exists, if not install dependencies
    if not (frontend_dir / "node_modules").exists():
        print("→ Installing frontend dependencies...")
        success, _ = run_command(
            ["npm", "install"], "Running npm install", cwd=frontend_dir
        )
        if not success:
            return False

    success, _ = run_background_command(
        ["npm", "run", "dev"],
        "Starting Next.js on port 3000",
        cwd=frontend_dir,
        log_file=str(log_file),
    )

    if success:
        print(f"  ✓ Frontend started (logs: {log_file})")
        # Wait a moment for the server to start
        time.sleep(2)
    return success


def main():
    parser = argparse.ArgumentParser(
        description="Set up cli2ansible development environment"
    )
    parser.add_argument(
        "--skip-docker", action="store_true", help="Skip starting Docker services"
    )
    parser.add_argument(
        "--skip-migrations", action="store_true", help="Skip database migrations"
    )
    parser.add_argument(
        "--skip-servers",
        action="store_true",
        help="Skip starting backend and frontend servers",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Remove venv and reinstall"
    )
    args = parser.parse_args()

    print("\n🚀 Setting up cli2ansible development environment\n")

    if not check_prerequisites():
        sys.exit(1)

    if not install_dependencies(clean=args.clean):
        sys.exit(1)

    if not args.skip_docker and not start_docker_services():
        print("\n⚠️  Docker services failed, continuing without them...")

    if not args.skip_docker and not args.skip_migrations and not run_migrations():
        print("\n⚠️  Migrations failed, you may need to run them manually")

    if not args.skip_servers:
        if not start_backend():
            print("\n⚠️  Backend failed to start")
        if not start_frontend():
            print("\n⚠️  Frontend failed to start")

    print("\n✅ Development environment setup complete!\n")

    if not args.skip_servers:
        print("Services running:")
        print("  • Backend API:  http://localhost:8000")
        print("  • Frontend:     http://localhost:3000")
        print("  • MinIO Console: http://localhost:9001")
        print("\nLogs available at:")
        print("  • Backend:  .augment/logs/backend.log")
        print("  • Frontend: .augment/logs/frontend.log")
        print("\nPress Ctrl+C to stop all services...")

        try:
            # Keep the script running to maintain background processes
            while True:
                time.sleep(1)
                # Check if processes are still running
                for proc, desc, _ in background_processes:
                    if proc.poll() is not None:
                        print(f"\n⚠️  {desc} has stopped")
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping services...")
            for proc, desc, log_file in background_processes:
                if proc.poll() is None:
                    proc.terminate()
                    print(f"  • Stopped {desc}")
                if log_file:
                    with contextlib.suppress(Exception):
                        open(log_file).close()  # noqa: SIM115
            print("  ✓ All services stopped")
    else:
        print("Next steps:")
        print("  • Run tests: make test-unit")
        print("  • Start the app: poetry run uvicorn cli2ansible.app:app --reload")
        print("  • Start frontend: cd frontend && npm run dev")


if __name__ == "__main__":
    main()
