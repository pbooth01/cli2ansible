# Augment Quick Start Guide

Get started with Augment Agent workflows in 5 minutes.

## 🚀 Common Tasks

### Review a Pull Request

**Simple review:**
```
Review PR #42
```

**Comprehensive review:**
```
Review PR #42 following .augment/workflows/pr-review.md

Focus on security and test coverage.
```

**Review current branch:**
```
Review my changes following .augment/workflows/pr-review.md
```

### Implement a Feature

**From description:**
```
Implement a new feature to add rate limiting to API endpoints.

Follow .augment/workflows/implement-feature.md
```

**From PRD:**
```
Implement the feature in docs/prds/rate-limiting.md

Follow .augment/workflows/implement-feature.md
```

### Fix Failing Tests

```
Fix the failing tests in tests/unit/test_services.py

Run the tests, identify the issues, and fix them.
```

### Refactor Code

```
Refactor src/cli2ansible/domain/services.py to improve readability.

Follow hexagonal architecture principles.
Maintain test coverage.
```

### Add Tests

```
Add comprehensive tests for src/cli2ansible/domain/services.py

Include:
- Unit tests
- Edge cases
- Error conditions
```

### Update Documentation

```
Update the documentation for the new API endpoints in src/cli2ansible/adapters/inbound/http/api.py

Include:
- Docstrings
- API documentation
- Examples
```

## 📋 Workflow Templates

### Code Review Template

```
Review [file/PR/branch] following .augment/workflows/pr-review.md

Check for:
- [x] Code quality
- [x] Security issues
- [x] Test coverage
- [x] Architecture compliance
- [ ] Performance issues
- [ ] Documentation
```

### Feature Implementation Template

```
Implement [feature description]

Follow .augment/workflows/implement-feature.md

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Acceptance Criteria:
- [ ] Feature works as expected
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Code reviewed
```

### Bug Fix Template

```
Fix bug: [description]

Steps:
1. Reproduce the bug
2. Identify root cause
3. Implement fix
4. Add regression test
5. Verify fix works
6. Update documentation if needed
```

## 🎯 Best Practices

### 1. Be Specific

❌ Bad:
```
Review this code
```

✅ Good:
```
Review src/cli2ansible/domain/services.py following .augment/workflows/pr-review.md

Focus on:
- Security vulnerabilities
- Test coverage for new methods
- Type safety
```

### 2. Reference Workflows

❌ Bad:
```
Implement a new feature
```

✅ Good:
```
Implement a new feature following .augment/workflows/implement-feature.md
```

### 3. Use Tasklists

❌ Bad:
```
Implement feature X, Y, and Z
```

✅ Good:
```
Implement the following features:

Create a tasklist and mark each as complete:
- [ ] Feature X
- [ ] Feature Y
- [ ] Feature Z
```

### 4. Provide Context

❌ Bad:
```
Fix the tests
```

✅ Good:
```
Fix the failing tests in tests/api/test_sessions.py

Context:
- Tests started failing after PR #42
- Error: "Field required [type=missing, input_value=...]"
- Likely related to SessionResponse schema changes
```

## 🔧 Configuration

### Customize PR Review

Edit `.augment/pr-review-config.json`:

```json
{
  "review_settings": {
    "min_coverage": 80,
    "fail_on_critical": true
  }
}
```

### Add Custom Workflow

1. Create `.augment/workflows/my-workflow.md`
2. Define steps and checklist
3. Reference in prompts:
   ```
   Follow .augment/workflows/my-workflow.md
   ```

## 💡 Tips & Tricks

### Tip 1: Use Memories

Ask Agent to remember preferences:
```
Remember: Always run tests before committing
Remember: Use type hints for all function parameters
Remember: Follow hexagonal architecture pattern
```

### Tip 2: Break Down Large Tasks

Instead of:
```
Implement the entire authentication system
```

Do:
```
Implement authentication system in phases:

Phase 1: User model and database schema
Phase 2: Password hashing and validation
Phase 3: JWT token generation
Phase 4: Authentication middleware
Phase 5: Tests and documentation
```

### Tip 3: Review Before Committing

```
Review my uncommitted changes following .augment/workflows/pr-review.md

Run all quality checks before committing.
```

### Tip 4: Use Quick Ask Mode

For read-only queries, use Quick Ask mode:
```
[Quick Ask] Explain how the session lifecycle works in this codebase
```

## 🆘 Troubleshooting

### Agent not following workflow

✅ Solution: Explicitly reference the workflow file
```
Follow the workflow in .augment/workflows/pr-review.md
```

### Steps being skipped

✅ Solution: Use tasklist to track progress
```
Create a tasklist for this work and mark each step complete
```

### Need more context

✅ Solution: Add files to context using @ symbol
```
@src/cli2ansible/domain/models.py Review this file for type safety issues
```

## 📚 Learn More

- [Full Documentation](.augment/README.md)
- [PR Review Workflow](.augment/workflows/pr-review.md)
- [Feature Implementation](.augment/workflows/implement-feature.md)
- [Project Conventions](../docs/conventions/)
