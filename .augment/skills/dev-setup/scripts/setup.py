#!/usr/bin/env python3
"""
Development Environment Setup Script

Sets up the complete development environment for cli2ansible:
1. Installs Python dependencies with Poetry
2. Starts Docker services (Postgres, MinIO)
3. Runs database migrations

Usage:
    python3 setup.py [--skip-docker] [--skip-migrations] [--clean]
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


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
            cwd=cwd
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n')[:5]:
                print(f"  {line}")
        return True, result
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False, e


def check_prerequisites():
    """Check that required tools are installed."""
    print("\n🔍 Checking prerequisites...\n")

    # Check Python version
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version}")
        return False
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
    success, _ = run_command(["docker", "compose", "version"], "Checking Docker Compose", check=False)
    if not success:
        success, _ = run_command(["docker-compose", "version"], "Checking docker-compose", check=False)
        if not success:
            print("  ❌ Docker Compose not found")
            return False
        compose_cmd = ["docker-compose"]
    else:
        compose_cmd = ["docker", "compose"]
    
    # Start services
    success, _ = run_command(compose_cmd + ["up", "-d", "postgres", "minio"], "Starting Postgres and MinIO")
    if not success:
        return False
    
    # Wait for services to be healthy
    print("→ Waiting for services to be healthy...")
    for _ in range(30):
        success, result = run_command(
            compose_cmd + ["ps", "--format", "json"],
            "Checking service status",
            check=False
        )
        time.sleep(2)
        break  # Services started, health check is handled by docker-compose
    
    print("  ✓ Docker services started")
    return True


def run_migrations():
    """Run database migrations."""
    print("\n🗃️  Running database migrations...\n")
    
    success, _ = run_command(
        ["poetry", "run", "alembic", "upgrade", "head"],
        "Running Alembic migrations"
    )
    return success


def main():
    parser = argparse.ArgumentParser(description="Set up cli2ansible development environment")
    parser.add_argument("--skip-docker", action="store_true", help="Skip starting Docker services")
    parser.add_argument("--skip-migrations", action="store_true", help="Skip database migrations")
    parser.add_argument("--clean", action="store_true", help="Remove venv and reinstall")
    args = parser.parse_args()

    print("\n🚀 Setting up cli2ansible development environment\n")
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not install_dependencies(clean=args.clean):
        sys.exit(1)
    
    if not args.skip_docker:
        if not start_docker_services():
            print("\n⚠️  Docker services failed, continuing without them...")
    
    if not args.skip_docker and not args.skip_migrations:
        if not run_migrations():
            print("\n⚠️  Migrations failed, you may need to run them manually")
    
    print("\n✅ Development environment setup complete!\n")
    print("Next steps:")
    print("  • Run tests: make test-unit")
    print("  • Start the app: poetry run uvicorn cli2ansible.app:app --reload")
    print("  • Start frontend: cd frontend && npm run dev")


if __name__ == "__main__":
    main()

