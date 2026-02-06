#!/usr/bin/env python3
"""
Code Quality Check Script

Runs linting (ruff), type checking (mypy), and formatting (black) for cli2ansible.

Usage:
    python3 check.py [OPTIONS]
"""

import argparse
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"   Command: {' '.join(cmd)}")
    print("=" * 60 + "\n")

    result = subprocess.run(cmd)
    return result.returncode == 0


def run_ruff(fix: bool = False, file_path: str | None = None) -> bool:
    """Run ruff linter."""
    cmd = ["poetry", "run", "ruff", "check"]

    if fix:
        cmd.append("--fix")

    if file_path:
        cmd.append(file_path)
    else:
        cmd.append(".")

    return run_command(cmd, "Running ruff linter" + (" (with --fix)" if fix else ""))


def run_mypy(file_path: str | None = None) -> bool:
    """Run mypy type checker."""
    cmd = ["poetry", "run", "mypy"]

    if file_path:
        cmd.append(file_path)
    else:
        cmd.append("src")

    return run_command(cmd, "Running mypy type checker")


def run_black(fix: bool = False, file_path: str | None = None) -> bool:
    """Run black formatter."""
    cmd = ["poetry", "run", "black"]

    if not fix:
        cmd.append("--check")

    if file_path:
        cmd.append(file_path)
    else:
        cmd.append(".")

    return run_command(
        cmd,
        "Running black formatter" + (" (applying fixes)" if fix else " (check only)"),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run code quality checks for cli2ansible"
    )
    parser.add_argument("--lint", action="store_true", help="Run only ruff linting")
    parser.add_argument(
        "--types", action="store_true", help="Run only mypy type checking"
    )
    parser.add_argument(
        "--format", action="store_true", help="Run only black formatting"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues (ruff and black)"
    )
    parser.add_argument(
        "--file", "-f", dest="file_path", help="Check specific file/directory"
    )

    args = parser.parse_args()

    # If no specific check requested, run all
    run_all = not (args.lint or args.types or args.format)

    results = {}

    print("\n🔧 Running code quality checks for cli2ansible\n")

    if run_all or args.lint:
        results["ruff"] = run_ruff(fix=args.fix, file_path=args.file_path)

    if run_all or args.types:
        results["mypy"] = run_mypy(file_path=args.file_path)

    if run_all or args.format:
        results["black"] = run_black(fix=args.fix, file_path=args.file_path)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)

    all_passed = True
    for tool, passed in results.items():
        status = "✅ Passed" if passed else "❌ Failed"
        print(f"   {tool}: {status}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("✅ All code quality checks passed!\n")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Run with --fix to auto-fix issues.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
