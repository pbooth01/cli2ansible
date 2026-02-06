---
name: git-refresh
description: Force refresh local workspace from GitHub by performing a complete hard reset to match the remote branch. Use when the user wants to discard all local changes and reset their workspace to match the remote state, clean up a messy workspace, or start fresh from the remote branch. Triggers on requests like "refresh from GitHub", "reset workspace to main", "clean up my workspace", "discard all changes and sync with remote", or "force pull from origin".
---

# Git Refresh

## Overview

This skill provides a safe, reliable way to completely refresh a local Git workspace from GitHub, discarding all local changes and resetting to match the remote branch state. It handles both the main repository and all submodules.

## When to Use

Use this skill when the user wants to:
- Discard all local changes and sync with remote
- Clean up a workspace that's in a messy state
- Reset to a known good state from GitHub
- Start fresh from the remote branch
- Force pull the latest changes, overwriting local modifications

## Usage

Simply run the refresh script:

```bash
python3 .augment/skills/git-refresh/scripts/refresh.py
```

### Options

- `--branch BRANCH`: Specify which branch to reset to (default: `main`)
- `--remote REMOTE`: Specify which remote to fetch from (default: `origin`)

### Examples

```bash
# Refresh from origin/main (default)
python3 .augment/skills/git-refresh/scripts/refresh.py

# Refresh from origin/develop
python3 .augment/skills/git-refresh/scripts/refresh.py --branch develop

# Refresh from upstream/main
python3 .augment/skills/git-refresh/scripts/refresh.py --branch main --remote upstream
```

## What It Does

The script performs these operations in sequence:

1. **Main Repository:**
   - Fetches latest from remote branch
   - Force checks out the branch (discarding local changes)
   - Hard resets to remote state
   - Cleans all untracked files and directories

2. **Submodules (if present):**
   - Initializes and updates all submodules
   - Fetches latest for each submodule
   - Force checks out the branch in each submodule
   - Hard resets each submodule
   - Cleans untracked files in each submodule

## Warnings

⚠️ **This operation is destructive!** It will discard:
- All uncommitted changes
- All untracked files
- Local branches that differ from remote
- Any work not pushed to the remote

Always ensure important work is committed and pushed before running this script.
