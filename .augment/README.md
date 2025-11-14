# Augment Configuration

This directory contains configuration and workflows for Augment Agent to help automate development tasks in the cli2ansible project.

## Structure

```
.augment/
├── README.md                          # This file
├── QUICK_START.md                     # Quick reference guide
├── context.json                       # Project context and configuration
├── rules/                             # Augment rules (auto-applied by Auggie CLI)
│   ├── architecture.md               # Hexagonal architecture compliance
│   ├── code-quality.md               # Code quality standards
│   ├── documentation.md              # Documentation requirements
│   ├── performance.md                # Performance best practices
│   ├── security.md                   # Security rules (critical)
│   └── testing.md                    # Testing requirements (≥80% coverage)
└── workflows/                         # Workflow definitions
    ├── pr-review.md                  # PR review automation
    └── implement-feature.md          # Feature implementation workflow
```

## Quick Start

### 1. PR Review

To get an automated code review on a PR:

```
Review PR #<number> following .augment/workflows/pr-review.md
```

Or set up automated reviews with GitHub Actions (see `workflows/pr-review.md`).

### 2. Feature Implementation

To implement a new feature:

```
Implement feature: <description>

Follow .augment/workflows/implement-feature.md
```

## Configuration Files

### Rules (`.augment/rules/`)

**Automatically applied by Auggie CLI** - No configuration needed!

All markdown files in `.augment/rules/` are automatically picked up and applied when running:
```bash
auggie --print "Review this PR"
```

Current rules:
- **architecture.md** - Hexagonal architecture, domain has no I/O, ports & adapters
- **code-quality.md** - Style, naming, complexity, error handling, type hints
- **documentation.md** - Docstrings, README updates, API docs, comments
- **performance.md** - No N+1 queries, efficient DB operations, async usage
- **security.md** - No secrets, input validation, injection prevention (CRITICAL)
- **testing.md** - ≥80% coverage, unit + integration tests, edge cases

### context.json

Contains project-wide context that Augment Agent uses:
- Project metadata
- Key files and conventions
- Testing configuration
- Quality check commands
- Quick reference commands

### Workflows

#### pr-review.md
Comprehensive PR review workflow covering:
- Code quality analysis
- Security review
- Test coverage analysis
- Architecture compliance
- Documentation check
- Performance review

#### implement-feature.md
End-to-end feature implementation workflow:
- Requirements analysis
- Branch management
- Implementation following hexagonal architecture
- Test generation
- Quality checks
- PR creation

## Usage Examples

### Example 1: Review a PR

```
Review PR #42 following the workflow in .augment/workflows/pr-review.md

Focus on:
- Security issues
- Test coverage
- Architecture compliance
```

### Example 2: Implement a Feature

```
Implement a new feature to add rate limiting to the API endpoints.

Follow .augment/workflows/implement-feature.md

Requirements:
- Add rate limiting middleware
- Configure limits per endpoint
- Add tests
- Update documentation
```

### Example 3: Quick Code Review

```
Review the changes in src/cli2ansible/domain/services.py

Check for:
- Code quality
- Type safety
- Test coverage
```

## Integration with GitHub Actions

### Automated PR Reviews

This project uses the official **`augmentcode/review-pr`** GitHub Action for automated PR reviews.

The action is configured in `.github/workflows/ci.yml` and automatically:
- ✅ Runs on every pull request
- ✅ Applies all rules from `.augment/rules/`
- ✅ Posts inline comments on specific lines
- ✅ Submits a GitHub review with findings

**Current configuration:**

```yaml
- name: Generate PR Review
  uses: augmentcode/review-pr@v0
  with:
    augment_session_auth: ${{ secrets.AUGMENT_SESSION_AUTH }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    pull_number: ${{ github.event.pull_request.number }}
    repo_name: ${{ github.repository }}
    rules: |
      [
        ".augment/rules/architecture.md",
        ".augment/rules/code-quality.md",
        ".augment/rules/security.md",
        ".augment/rules/testing.md",
        ".augment/rules/documentation.md",
        ".augment/rules/performance.md"
      ]
```

**Required GitHub Secret:**
- `AUGMENT_SESSION_AUTH` - Get this from `auggie tokens print` or `~/.augment/session.json`

## Customization

### Adding New Rules

1. Create `.augment/rules/my-rule.md`
2. Define rules with severity and examples:
   ```markdown
   # My Custom Rule

   ## Rules

   ### 1. Rule Name
   - **Severity**: Warning/Critical
   - **Description**: What this rule checks

   **Example - Bad**:
   ```python
   # Bad code
   ```

   **Example - Good**:
   ```python
   # Good code
   ```
   ```
3. **Rules are automatically applied** by Auggie CLI!

### Adding New Workflows

1. Create a new markdown file in `.augment/workflows/`
2. Define the workflow steps and checklist
3. Reference it in `context.json` under `workflows`

### Updating Context

Edit `.augment/context.json` to:
- Add new key files
- Update conventions
- Modify quality check commands
- Add quick references

## Best Practices

1. **Keep workflows focused** - Each workflow should have a single, clear purpose
2. **Use checklists** - Make it easy for Agent to verify completion
3. **Reference conventions** - Point to existing documentation
4. **Be specific** - Provide clear, actionable steps
5. **Update regularly** - Keep workflows in sync with project changes

## Memories

Augment Agent automatically stores memories in `.augment/memories/` to remember:
- Project preferences
- Common patterns
- Frequently used commands
- Team conventions

These memories help Agent provide more contextual and relevant assistance over time.

## Troubleshooting

### Agent not following workflow

Make sure to explicitly reference the workflow file:
```
Follow the workflow in .augment/workflows/<workflow-name>.md
```

### Workflow steps being skipped

Use the tasklist feature to track progress:
```
Create a tasklist for implementing this feature following .augment/workflows/implement-feature.md
```

### Need to customize a workflow

Copy the workflow file and modify it:
```bash
cp .augment/workflows/pr-review.md .augment/workflows/pr-review-custom.md
# Edit the custom workflow
```

Then reference your custom workflow:
```
Review this PR following .augment/workflows/pr-review-custom.md
```

## Contributing

When adding new workflows or updating configuration:

1. Test the workflow with Augment Agent
2. Document any new features in this README
3. Update `context.json` if needed
4. Submit a PR with your changes

## Resources

- [Augment Documentation](https://docs.augmentcode.com)
- [Project Conventions](../docs/conventions/)
- [GitHub Workflows](../.github/workflows/)
