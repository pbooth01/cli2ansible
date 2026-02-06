---
name: dev-setup
description: Set up the cli2ansible development environment. Installs Python dependencies with Poetry, starts Docker services (Postgres, MinIO), and runs database migrations. Use when starting work on the project, after cloning, or when the dev environment needs to be reset. Triggers on requests like "set up dev environment", "install dependencies", "initialize the project", or "get the project running".
---

# Development Environment Setup

## Overview

This skill sets up a complete development environment for the cli2ansible project, including Python dependencies, Docker services, and database migrations.

## When to Use

Use this skill when:
- Setting up the project for the first time after cloning
- Resetting the development environment
- After major dependency changes
- When Docker services need to be restarted fresh

## Usage

```bash
python3 .augment/skills/dev-setup/scripts/setup.py
```

### Options

- `--skip-docker`: Skip starting Docker services
- `--skip-migrations`: Skip running database migrations
- `--clean`: Remove existing virtual environment and start fresh

### Examples

```bash
# Full setup (dependencies + docker + migrations)
python3 .augment/skills/dev-setup/scripts/setup.py

# Only install dependencies (skip docker and migrations)
python3 .augment/skills/dev-setup/scripts/setup.py --skip-docker --skip-migrations

# Clean setup (remove venv and reinstall everything)
python3 .augment/skills/dev-setup/scripts/setup.py --clean
```

## What It Does

1. **Dependencies**:
   - Checks for Poetry installation
   - Installs all development dependencies via `poetry install`

2. **Docker Services** (unless skipped):
   - Starts PostgreSQL database
   - Starts MinIO (S3-compatible storage)
   - Waits for services to be healthy

3. **Database Migrations** (unless skipped):
   - Runs Alembic migrations to set up the database schema

## Prerequisites

- Python 3.11+
- Poetry installed (`pip install poetry`)
- Docker and docker-compose installed (if using Docker services)

