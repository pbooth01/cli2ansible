---
name: run-tests
description: Run pytest tests for the cli2ansible project with various options. Supports unit tests, integration tests, specific test files, coverage reports, and verbose output. Use when you need to run tests, verify changes, or check code coverage. Triggers on requests like "run tests", "run unit tests", "test this file", "check coverage", or "run integration tests".
---

# Run Tests

## Overview

This skill provides a convenient way to run pytest tests for the cli2ansible project with various filtering and output options.

## When to Use

Use this skill when:
- Running all tests to verify changes
- Running only unit tests (fast feedback)
- Running integration tests (requires Docker services)
- Testing a specific file or test function
- Generating coverage reports

## Usage

```bash
poetry run python .augment/skills/run-tests/scripts/run_tests.py [OPTIONS]
```

Or use the Makefile shortcuts:
```bash
make test-unit      # Run unit tests only
make test           # Run all tests with coverage
```

### Options

- `--unit`: Run only unit tests (skip integration tests)
- `--integration`: Run only integration tests
- `--file FILE`: Run tests in a specific file
- `--test TEST`: Run a specific test by name pattern (uses pytest -k)
- `--coverage`: Generate HTML coverage report
- `--verbose` / `-v`: Verbose output
- `--fail-fast` / `-x`: Stop on first failure

### Examples

```bash
# Run all tests
poetry run python .augment/skills/run-tests/scripts/run_tests.py

# Run only unit tests (fast)
poetry run python .augment/skills/run-tests/scripts/run_tests.py --unit

# Run integration tests
poetry run python .augment/skills/run-tests/scripts/run_tests.py --integration

# Run a specific test file
poetry run python .augment/skills/run-tests/scripts/run_tests.py --file tests/unit/test_models.py

# Run tests matching a pattern
poetry run python .augment/skills/run-tests/scripts/run_tests.py --test "test_session"

# Run with coverage and stop on first failure
poetry run python .augment/skills/run-tests/scripts/run_tests.py --coverage -x

# Verbose unit tests
poetry run python .augment/skills/run-tests/scripts/run_tests.py --unit -v
```

## Test Categories

- **Unit tests**: Fast tests that don't require external services (Postgres, MinIO)
- **Integration tests**: Tests that require Docker services running

## Coverage

Coverage reports are generated in `htmlcov/` directory. Open `htmlcov/index.html` to view.

