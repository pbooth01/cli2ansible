# Claude Code → Auto-merge Workflow

Complete workflow for building features with Claude Code that automatically merge when tests pass.

## 🎯 Overview

1. **You**: Give Claude a PRD
2. **Claude**: Builds feature (code + tests + docs)
3. **Claude**: Creates branch, commits, pushes, opens PR
4. **GitHub CI**: Runs tests automatically
5. **GitHub**: Auto-merges if tests pass ✅

## 📋 Prerequisites

### One-Time Setup (You Do This Once)

1. **Configure branch protection** (follow [.github/BRANCH_PROTECTION.md](../.github/BRANCH_PROTECTION.md))
   - Protect `release` branch
   - Require CI checks
   - Enable auto-merge (0 or 1 approval)

2. **Verify CI works**
   ```bash
   git checkout -b test-ci
   touch test.txt
   git add test.txt
   git commit -m "test: verify CI"
   git push -u origin test-ci
   # Create PR to 'release', watch CI run
   ```

3. **Grant Claude access to git** (Claude Code can run bash commands)

## 🚀 The Workflow

### Step 1: Give Claude a PRD

```text
Load .claude/context.json
Load docs/prds/TEMPLATE.md

I want to build this feature:
<describe feature OR paste PRD>

Follow this workflow:
1. Create implementation plan
2. Build feature with tests
3. Create branch feat/feature-name
4. Commit with conventional commits
5. Push and create PR to release branch

Do NOT merge manually - let auto-merge handle it.
```

### Step 2: Claude Implements

Claude will:
- ✅ Create implementation plan
- ✅ Write code following conventions
- ✅ Generate tests (using test-agent)
- ✅ Run security review (using security-agent)
- ✅ Create documentation
- ✅ Run local tests (`make test`)
- ✅ Create feature branch
- ✅ Make commits with conventional commit messages
- ✅ Push to remote
- ✅ Create PR via `gh` CLI

### Step 3: GitHub Takes Over

**Automatic GitHub Actions:**

1. **CI Workflow** (.github/workflows/ci.yml)
   - Installs dependencies
   - Runs linting (ruff, mypy)
   - Runs tests with coverage
   - Reports results

2. **Auto-merge Workflow** (.github/workflows/auto-merge.yml)
   - Waits for CI to complete
   - If CI passes: Enables auto-merge
   - Comments on PR with status
   - Merges automatically (if approvals met)

### Step 4: Merged! 🎉

- Feature is in `release` branch
- Tests passed
- No manual intervention needed

## 📝 Example Session

### You Say:

```text
Load .claude/context.json

Build a new feature from this PRD:

Feature: Add systemctl restart support
- Translate "systemctl restart <service>" to Ansible systemd module
- Handle with 'restarted' state
- Add tests
- High confidence translation

Create branch, commit, push, and open PR. Enable auto-merge.
```

### Claude Does:

```bash
# 1. Create plan
echo "Implementation plan:
1. Update rules_engine.py with restart pattern
2. Add tests in test_translator.py
3. Update documentation
"

# 2. Implement feature
# ... creates/edits files ...

# 3. Run tests locally
make test
make lint

# 4. Create branch
git checkout -b feat/systemctl-restart-support

# 5. Commit
git add -A
git commit -m "feat: add systemctl restart translation

- Add restart action support to systemctl rule
- Map to systemd module with restarted state
- Add unit tests for restart command
- Update translator documentation

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push
git push -u origin feat/systemctl-restart-support

# 7. Create PR
gh pr create \
  --title "feat: add systemctl restart translation" \
  --body "$(cat <<'EOF'
## Summary
Adds support for `systemctl restart` command translation.

## Changes
- Updated rules_engine.py with restart pattern
- Added unit tests for restart scenario
- Updated documentation

## Testing
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Lint and type checks pass

## Translation Example
\`\`\`bash
# Command
systemctl restart nginx

# Ansible Task
- name: Restart service nginx
  systemd:
    name: nginx
    state: restarted
\`\`\`

🤖 Generated with Claude Code
EOF
)" \
  --base release
```

### GitHub Actions:

```
✅ CI: build (passed in 2m 34s)
✅ Auto-merge: Enabled
✅ Merged to release
```

### You:

☕ Drink coffee. Feature is done!

## 🔧 Customizing the Workflow

### Option 1: Require Manual Approval

In branch protection settings:
- Set "Require approvals" to **1**

Now:
```
[PR Created] → [CI Passes] → [You Approve] → ✅ Auto-merge
```

### Option 2: No Auto-merge (Manual Only)

Delete `.github/workflows/auto-merge.yml`

Now:
```
[PR Created] → [CI Passes] → [You Manually Merge]
```

### Option 3: Auto-merge to Main Too

Add workflow for `main` branch:

```yaml
# .github/workflows/auto-merge-main.yml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
# ... (similar to auto-merge.yml)
```

## 🛡️ Safety Mechanisms

### Built-in Safeguards

1. **CI Must Pass**: PR won't merge if tests fail
2. **Conventional Commits**: Enforced by pre-commit
3. **Code Review**: Optional human approval
4. **Branch Protection**: Can't push directly to `release`
5. **Security Agent**: Claude runs security review first

### When Auto-merge is Skipped

Auto-merge **won't run** if:
- ❌ Branch doesn't match pattern (`feat/`, `fix/`, `docs/`)
- ❌ CI fails
- ❌ Approval required but not given
- ❌ Branch is out of date
- ❌ Conversations not resolved

## 🚨 Rollback Procedure

If bad code gets merged:

```bash
# 1. Find the merge commit
git log --oneline -10

# 2. Revert the merge
git revert -m 1 <merge-commit-sha>

# 3. Push
git push origin release

# 4. Open PR with revert
gh pr create --title "Revert: <bad feature>" --base release
```

## 📊 Monitoring

### Check PR Status

```bash
gh pr status
gh pr view <number>
gh pr checks <number>
```

### View CI Logs

```bash
gh run list
gh run view <run-id> --log
```

### List Auto-merged PRs

```bash
gh pr list --state merged --search "auto-merged"
```

## 💡 Pro Tips

### Speed Up Development

Use Claude's multi-tasking:

```text
Load .claude/context.json

I have 3 PRDs to implement:
1. <PRD 1>
2. <PRD 2>
3. <PRD 3>

For each:
- Create separate branch
- Implement feature
- Push and open PR

Do them in parallel if possible.
```

### Batch Related Changes

```text
Load .claude/context.json

Build these related features in ONE PR:
- Feature A
- Feature B
- Shared tests

Branch: feat/combined-feature
```

### Hot Fix Workflow

```text
Load .claude/context.json

URGENT: Fix this bug:
<bug description>

Use branch: fix/urgent-bug-name
Fast-track: Skip optional checks, focus on fix + test.
```

## 🤔 FAQs

**Q: Can Claude merge directly to main?**
A: No (and shouldn't). Always go through `release` → CI → auto-merge.

**Q: What if tests fail?**
A: Auto-merge won't trigger. Claude can fix and push updates.

**Q: Can I stop auto-merge mid-flight?**
A: Yes, disable auto-merge on the PR or close it.

**Q: Does this work for external contributors?**
A: Yes, but they need proper repo permissions.

**Q: Can I require code review AND auto-merge?**
A: Yes! Set branch protection to require 1 approval.

## 🎓 Best Practices

### ✅ Do

- Keep PRs small and focused
- Use conventional commit messages
- Run tests locally before pushing
- Review Claude's code before committing
- Use descriptive branch names

### ❌ Don't

- Mix multiple features in one PR
- Skip local testing
- Force-push to PR branches (breaks auto-merge)
- Merge without waiting for CI
- Bypass branch protection

## 📚 Related Docs

- [Branch Protection Setup](../.github/BRANCH_PROTECTION.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Claude Code Guide](CLAUDE_CODE_GUIDE.md)
- [CI Workflow](../.github/workflows/ci.yml)
- [Auto-merge Workflow](../.github/workflows/auto-merge.yml)

---

🤖 **Happy auto-merging with Claude Code!**
