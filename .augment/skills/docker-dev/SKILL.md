---
name: docker-dev
description: Manage Docker development services for cli2ansible (Postgres, MinIO, app, frontend). Start, stop, restart services, view logs, and check status. Use when you need to control Docker containers for local development. Triggers on requests like "start docker", "stop services", "show docker logs", "restart the app", "check service status", or "clean docker volumes".
---

# Docker Development Environment

## Overview

This skill manages the Docker Compose development environment for cli2ansible, including PostgreSQL, MinIO (S3-compatible storage), the FastAPI backend, and the Next.js frontend.

## When to Use

Use this skill when:
- Starting the development environment
- Stopping services when done working
- Viewing logs to debug issues
- Restarting services after configuration changes
- Checking the status of running services
- Cleaning up Docker volumes for a fresh start

## Usage

```bash
python3 .augment/skills/docker-dev/scripts/docker.py <command> [OPTIONS]
```

### Commands

- `up`: Start services
- `down`: Stop services
- `restart`: Restart services
- `logs`: View service logs
- `status`: Show service status
- `clean`: Stop services and remove volumes

### Options

- `--service SERVICE`: Target a specific service (postgres, minio, app, web)
- `--follow / -f`: Follow log output (for `logs` command)
- `--tail N`: Number of log lines to show (default: 100)

### Examples

```bash
# Start all services
python3 .augment/skills/docker-dev/scripts/docker.py up

# Start only backend services (postgres + minio)
python3 .augment/skills/docker-dev/scripts/docker.py up --service postgres --service minio

# View app logs (follow mode)
python3 .augment/skills/docker-dev/scripts/docker.py logs --service app -f

# Check status of all services
python3 .augment/skills/docker-dev/scripts/docker.py status

# Restart the app after code changes
python3 .augment/skills/docker-dev/scripts/docker.py restart --service app

# Stop everything
python3 .augment/skills/docker-dev/scripts/docker.py down

# Clean up and start fresh
python3 .augment/skills/docker-dev/scripts/docker.py clean
```

## Services

| Service  | Port  | Description                    |
|----------|-------|--------------------------------|
| postgres | 5432  | PostgreSQL database            |
| minio    | 9000  | MinIO S3-compatible storage    |
| minio    | 9001  | MinIO web console              |
| app      | 8000  | FastAPI backend                |
| web      | 3000  | Next.js frontend               |

## Access URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

