#!/usr/bin/env python3
"""
Git Refresh Script - Force refresh local workspace from GitHub

This script performs a complete hard reset of the local workspace to match
the remote main branch, including all submodules. It's useful for cleaning
up a workspace that has gotten into a messy state.

WARNING: This will discard ALL local changes, including:
- Uncommitted changes
- Untracked files
- Local branches that differ from remote

Usage:
    python3 refresh.py [--branch BRANCH] [--remote REMOTE]

Arguments:
    --branch BRANCH    Branch to reset to (default: main)
    --remote REMOTE    Remote to fetch from (default: origin)

Examples:
    python3 refresh.py
    python3 refresh.py --branch develop
    python3 refresh.py --branch main --remote upstream
"""

import argparse
import subprocess
import sys


def run_command(cmd, description, cwd=None):
    """
    Run a shell command and handle errors.

    Args:
        cmd: Command to run (string or list)
        description: Human-readable description of what the command does
        cwd: Working directory (defaults to current directory)

    Returns:
        True if successful, False otherwise
    """
    print(f"→ {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(
                cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd
            )
        else:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=cwd
            )

        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False


def refresh_workspace(branch="main", remote="origin"):
    """
    Perform a complete hard reset of the workspace to match remote.

    Args:
        branch: Branch name to reset to
        remote: Remote name to fetch from

    Returns:
        True if successful, False otherwise
    """
    print(f"\n🔄 Refreshing workspace from {remote}/{branch}\n")
    print("⚠️  WARNING: This will discard ALL local changes!\n")

    # Main repository refresh
    commands = [
        (f"git fetch {remote} {branch}", f"Fetching latest from {remote}/{branch}"),
        (
            f"git checkout --force -B {branch} {remote}/{branch}",
            f"Force checking out {branch}",
        ),
        ("git reset --hard", "Hard resetting to remote state"),
        ("git clean -fdx", "Cleaning untracked files and directories"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print("\n❌ Failed to refresh main repository")
            return False

    # Check if there are submodules
    try:
        result = subprocess.run(
            ["git", "config", "--file", ".gitmodules", "--get-regexp", "path"],
            capture_output=True,
            text=True,
            check=False,
        )
        has_submodules = result.returncode == 0 and result.stdout.strip()
    except Exception:
        has_submodules = False

    if has_submodules:
        print("\n📦 Refreshing submodules...\n")

        submodule_commands = [
            (
                "git submodule update --init --recursive --force",
                "Initializing and updating submodules",
            ),
            ("git submodule foreach git fetch", "Fetching latest for all submodules"),
            (
                f"git submodule foreach git checkout --force -B {branch} {remote}/{branch}",
                f"Checking out {branch} in submodules",
            ),
            ("git submodule foreach git reset --hard", "Hard resetting submodules"),
            ("git submodule foreach git clean -fdx", "Cleaning submodules"),
        ]

        for cmd, desc in submodule_commands:
            if not run_command(cmd, desc):
                print("\n⚠️  Warning: Failed to refresh submodules (continuing anyway)")
                break

    print("\n✅ Workspace refresh complete!\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Force refresh local workspace from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Refresh from origin/main
  %(prog)s --branch develop             # Refresh from origin/develop
  %(prog)s --branch main --remote upstream  # Refresh from upstream/main
        """,
    )
    parser.add_argument(
        "--branch", default="main", help="Branch to reset to (default: main)"
    )
    parser.add_argument(
        "--remote", default="origin", help="Remote to fetch from (default: origin)"
    )

    args = parser.parse_args()

    # Verify we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    # Perform the refresh
    success = refresh_workspace(branch=args.branch, remote=args.remote)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
