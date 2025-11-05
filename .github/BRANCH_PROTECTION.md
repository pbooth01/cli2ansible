# Branch Protection Setup



To enable auto-merge on successful CI, configure these branch protection rules in GitHub.

## Setup Instructions

1. Go to: `Settings` → `Branches` → `Add rule`
2. Configure for `release` branch

## Required Settings

### Branch name pattern
```
release
```

### Protect matching branches

#### ✅ Require a pull request before merging
- ☑ Require approvals: **0** (for auto-merge without human approval)
  - *OR set to 1 if you want manual approval before auto-merge*
- ☑ Dismiss stale pull request approvals when new commits are pushed
- ☐ Require review from Code Owners (optional)

#### ✅ Require status checks to pass before merging
- ☑ Require branches to be up to date before merging
- **Required status checks:**
  - `build` (from ci.yml)

#### ✅ Require conversation resolution before merging
- ☑ All conversations must be resolved

#### ✅ Do not allow bypassing the above settings
- ☑ Include administrators (recommended)

### Allow force pushes
- ☐ Do not allow force pushes

### Allow deletions
- ☐ Do not allow branch deletion

## Auto-merge Configuration

### In Repository Settings

1. Go to: `Settings` → `General` → `Pull Requests`
2. Enable: ☑ **Allow auto-merge**
3. Choose default merge method: **Squash merging** (recommended)

## How Auto-merge Works

### With No Approval Required (approvals: 0)

```
[PR Created] → [CI Runs] → [CI Passes] → ✅ Auto-merge
```

### With Approval Required (approvals: 1)

```
[PR Created] → [CI Runs] → [CI Passes] → [Human Approves] → ✅ Auto-merge
```

## Testing the Setup

1. Create a test branch:
   ```bash
   git checkout -b feat/test-auto-merge
   ```

2. Make a trivial change:
   ```bash
   echo "# Test" >> docs/test.md
   git add docs/test.md
   git commit -m "feat: test auto-merge"
   git push -u origin feat/test-auto-merge
   ```

3. Create PR to `release` branch

4. Watch for:
   - CI runs automatically
   - Auto-merge workflow comments on PR
   - PR auto-merges when CI passes (and approved if required)

## For Main Branch

Repeat the same settings for `main` branch, but with PRs from `release`:

- Branch name pattern: `main`
- Same protection rules
- PRs must come from `release` branch

## Troubleshooting

### Auto-merge not triggering

1. Check workflow file: `.github/workflows/auto-merge.yml`
2. Verify branch name starts with `feat/`, `fix/`, or `docs/`
3. Check GitHub Actions logs for errors
4. Ensure `GITHUB_TOKEN` has write permissions

### CI not running

1. Check `.github/workflows/ci.yml` exists
2. Verify branch name pattern matches (`release`)
3. Check Actions permissions: `Settings` → `Actions` → `General` → `Workflow permissions`

### Auto-merge enabled but not merging

1. Check if approval is required (branch protection settings)
2. Verify all required status checks passed
3. Ensure branch is up to date with base branch
4. Check if conversations are resolved

## Security Notes

- ⚠️ Setting approvals to 0 allows code to merge without human review
- 💡 Recommended: Keep approvals at 1 for production repositories
- 🔒 Include administrators in restrictions for consistency
- 🤖 Auto-merge is useful for trusted automated workflows (e.g., Claude Code)

## Alternative: Manual Auto-merge

If you prefer more control, skip the workflow and use GitHub's built-in auto-merge:

1. Create PR manually
2. Click "Enable auto-merge" button in PR
3. PR merges automatically when CI passes (and approved if required)

## Updating This Document

If you change branch protection rules, update this document to match.
