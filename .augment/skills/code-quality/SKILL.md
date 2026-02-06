---
name: code-quality
description: Run code quality checks for the cli2ansible project including linting (ruff), type checking (mypy), and formatting (black). Can run all checks or individual tools, and optionally auto-fix issues. Use before committing code or when you need to check/fix code quality issues. Triggers on requests like "run linter", "check types", "format code", "run code quality checks", "fix linting errors", or "check code style".
---

# Code Quality Checks

## Overview

This skill runs code quality tools for the cli2ansible project: ruff (linting), mypy (type checking), and black (formatting).

## When to Use

Use this skill when:
- Before committing code changes
- After making significant code changes
- To auto-fix linting and formatting issues
- To check for type errors
- As part of a pre-PR checklist

## Usage

```bash
python3 .augment/skills/code-quality/scripts/check.py [OPTIONS]
```

### Options

- `--lint`: Run only ruff linting
- `--types`: Run only mypy type checking
- `--format`: Run only black formatting check
- `--fix`: Auto-fix linting and formatting issues
- `--file FILE`: Check only a specific file or directory

### Examples

```bash
# Run all checks (lint, types, format)
python3 .augment/skills/code-quality/scripts/check.py

# Auto-fix linting and formatting issues
python3 .augment/skills/code-quality/scripts/check.py --fix

# Run only linting
python3 .augment/skills/code-quality/scripts/check.py --lint

# Run only type checking
python3 .augment/skills/code-quality/scripts/check.py --types

# Check and fix a specific file
python3 .augment/skills/code-quality/scripts/check.py --fix --file src/cli2ansible/app.py

# Check the entire src directory
python3 .augment/skills/code-quality/scripts/check.py --file src/
```

## Tools Used

- **ruff**: Fast Python linter (replaces flake8, isort, and more)
- **mypy**: Static type checker for Python
- **black**: Opinionated code formatter

## Configuration

All tool configurations are in `pyproject.toml`:
- ruff: line-length=100, Python 3.11 target
- mypy: strict mode enabled
- black: default settings

