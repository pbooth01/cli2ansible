#!/usr/bin/env python3
"""
Test Runner Script

Runs pytest tests for cli2ansible with various options.

Usage:
    poetry run python run_tests.py [OPTIONS]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_poetry_available() -> bool:
    """Check if poetry is available."""
    try:
        result = subprocess.run(
            ["poetry", "--version"], capture_output=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_tests(
    unit_only: bool = False,
    integration_only: bool = False,
    file_path: str | None = None,
    test_pattern: str | None = None,
    coverage: bool = False,
    verbose: bool = False,
    fail_fast: bool = False,
) -> int:
    """Run pytest with the specified options."""

    cmd = ["poetry", "run", "pytest"]

    # Test selection
    if unit_only:
        cmd.extend(["-m", "not integration"])
        print("🧪 Running unit tests only...\n")
    elif integration_only:
        cmd.extend(["-m", "integration"])
        print("🧪 Running integration tests only...\n")
    else:
        print("🧪 Running all tests...\n")

    # Specific file
    if file_path:
        if not Path(file_path).exists():
            print(f"❌ Test file not found: {file_path}")
            return 1
        cmd.append(file_path)
        print(f"   File: {file_path}")

    # Test pattern (-k)
    if test_pattern:
        cmd.extend(["-k", test_pattern])
        print(f"   Pattern: {test_pattern}")

    # Coverage
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        print("   Coverage: enabled")

    # Verbose
    if verbose:
        cmd.append("-v")

    # Fail fast
    if fail_fast:
        cmd.append("-x")
        print("   Fail fast: enabled")

    print(f"\n   Command: {' '.join(cmd)}\n")
    print("-" * 60)

    # Run tests
    result = subprocess.run(cmd)

    print("-" * 60)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if coverage:
            print("\n📊 Coverage report: htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed (exit code: {result.returncode})")

    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run pytest tests for cli2ansible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--file", "-f", dest="file_path", help="Run tests in a specific file"
    )
    parser.add_argument(
        "--test", "-t", dest="test_pattern", help="Run tests matching pattern"
    )
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--fail-fast", "-x", action="store_true", help="Stop on first failure"
    )

    args = parser.parse_args()

    if args.unit and args.integration:
        print("❌ Cannot specify both --unit and --integration")
        sys.exit(1)

    exit_code = run_tests(
        unit_only=args.unit,
        integration_only=args.integration,
        file_path=args.file_path,
        test_pattern=args.test_pattern,
        coverage=args.coverage,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    if not check_poetry_available():
        print("❌ Poetry not found. Please install Poetry first:")
        print("   pip install poetry")
        print("\nThen run this script with:")
        print("   poetry run python .augment/skills/run-tests/scripts/run_tests.py")
        sys.exit(1)
    main()
