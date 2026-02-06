---
name: api-test
description: Test the cli2ansible API endpoints by creating sessions, ingesting cast files, and compiling Ansible playbooks. Useful for manual testing and debugging the full workflow. Use when you need to test the API, debug an endpoint, or demonstrate the application flow. Triggers on requests like "test the API", "ingest a cast file", "create a session", "compile a playbook", or "check API health".
---

# API Testing

## Overview

This skill provides commands to test the cli2ansible API endpoints, including health checks, session creation, cast file ingestion, and playbook compilation.

## When to Use

Use this skill when:
- Testing the API after code changes
- Debugging API endpoints
- Demonstrating the application workflow
- Ingesting sample cast files for testing
- Verifying the full ingest → compile pipeline

## Usage

```bash
python3 .augment/skills/api-test/scripts/api_test.py <command> [OPTIONS]
```

### Commands

- `health`: Check API health
- `create-session`: Create a new session
- `ingest`: Ingest a .cast file into a session
- `compile`: Compile a session into an Ansible playbook
- `full-demo`: Run the full demo workflow

### Options

- `--api-url URL`: API base URL (default: http://localhost:8000)
- `--session-id ID`: Session ID (for ingest/compile commands)
- `--cast-file FILE`: Path to .cast file (for ingest command)
- `--name NAME`: Session name (for create-session)

### Examples

```bash
# Check if API is healthy
python3 .augment/skills/api-test/scripts/api_test.py health

# Create a new session
python3 .augment/skills/api-test/scripts/api_test.py create-session --name "My Test Session"

# Ingest a cast file
python3 .augment/skills/api-test/scripts/api_test.py ingest --session-id <UUID> --cast-file tests/fixtures/demo.cast

# Compile to Ansible playbook
python3 .augment/skills/api-test/scripts/api_test.py compile --session-id <UUID>

# Run full demo (create → ingest → compile)
python3 .augment/skills/api-test/scripts/api_test.py full-demo --cast-file tests/fixtures/demo.cast
```

## Prerequisites

- API server must be running (http://localhost:8000)
- Use `docker-dev up` or `poetry run uvicorn cli2ansible.app:app --reload`

## Sample Cast Files

Test cast files are available in:
- `tests/fixtures/demo.cast`
- `tests/fixtures/phil-simple-demo/`

