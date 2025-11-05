---
description: Generate a complete feature implementation workflow from PRD to PR
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), Glob(*), Grep(*), Task(*), TodoWrite(*), WebFetch(*), WebSearch(*)
---

# Implement Feature

You are a feature implementation orchestrator for the cli2ansible project.

## Your Task
Generate and execute a complete workflow to implement a feature from PRD through to PR creation, using specialized agents and ensuring all quality checks pass.

## Context Setup
First, gather project context:

1. Read `VERSION` file to determine release branch (`release-<version>`)
2. Read the PRD content (user will provide path or text)
3. Load specialized agent definitions from `prompts/agents/`

## Implementation Workflow

### Step 1: Planning
- Use TodoWrite to create a detailed implementation plan
- Break down the PRD into specific tasks
- Identify files to create/modify
- Plan test strategy

### Step 2: Branch Management
```bash
git checkout -b feature/<descriptive-name>
```
Target merge branch: `release-<version>` (from VERSION file)

### Step 3: Implementation
Follow hexagonal architecture:
- Domain logic: `src/cli2ansible/domain/`
- Adapters: `src/cli2ansible/adapters/`
- Ports/interfaces for dependencies

Key principles:
- Keep changes focused
- Follow existing patterns
- Maintain type safety
- Write self-documenting code

### Step 4: Test Generation (Delegate to TestAgent)
After core implementation, use the Task tool:

```
Use Task tool with general-purpose agent:

"Read prompts/agents/test-agent.yaml to understand TestAgent's role and responsibilities.

Acting as TestAgent, analyze the following changes and generate comprehensive tests:

<provide git diff output>

Follow the TestAgent checklist:
- Identify all public interfaces changed
- Generate unit tests for domain logic (mock all adapters)
- Generate integration tests for adapter implementations
- Generate API tests if endpoints were modified
- Provide complete test files ready to implement

Return tests following the output schema in test-agent.yaml"
```

Implement the generated tests.

### Step 5: Security Review (Delegate to SecurityAgent)
Before committing, use the Task tool:

```
Use Task tool with general-purpose agent:

"Read prompts/agents/security-agent.yaml to understand SecurityAgent's role.

Acting as SecurityAgent, perform security review of these changes:

<provide git diff output>

Follow SecurityAgent's checklist:
- Secrets management
- Input validation
- Authentication/authorization
- Data protection
- Injection attacks (SQL, command, path traversal)
- Dependency vulnerabilities

Return findings with severity rankings and specific remediation steps."
```

Address any Critical or High severity findings immediately.

### Step 6: Quality Checks
Run all checks in this exact order:

```bash
make format      # Auto-fix formatting with ruff & black
make lint        # Check code quality with ruff
make type-check  # Verify type safety with mypy
make test        # Run pytest with coverage
```

**Critical:** All checks must pass. If any fail:
1. Fix the issues
2. Re-run ALL checks from the beginning
3. Do not proceed until everything passes

### Step 7: Documentation (If Needed)
If you modified APIs or architecture, delegate to DocumentationAgent:

```
Use Task tool with general-purpose agent:

"Read prompts/agents/documentation-agent.yaml.

Acting as DocumentationAgent, document these changes:

<describe what changed>

Generate appropriate documentation (API docs, architecture diagrams, user guides)."
```

### Step 8: Commit
```bash
git add .
git commit -m "<type>: <concise description>

<detailed explanation of changes>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

Commit types: feat, fix, refactor, test, docs, chore

### Step 9: Push
```bash
git push -u origin <branch-name>
```

### Step 10: Create PR
```bash
gh pr create --title "<feature-title>" \
  --body "$(cat <<'EOF'
## Summary
- <bullet point 1>
- <bullet point 2>

## Changes
<list of files and what changed>

## Test Plan
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing (make test)
- [ ] Code coverage maintained/improved

## Security Review
<summary of SecurityAgent findings and how addressed>

## Checklist
- [ ] Tests written and passing
- [ ] Lint checks passing (make lint)
- [ ] Type checks passing (make type-check)
- [ ] Code formatted (make format)
- [ ] Security review completed
- [ ] Documentation updated (if needed)

🤖 Generated with Claude Code
EOF
)" \
  --base release-<version>
```

## Project Context
- **Language:** Python 3.11+
- **Package Manager:** Poetry
- **Architecture:** Hexagonal (ports & adapters pattern)
- **Database:** SQLAlchemy with PostgreSQL
- **API:** FastAPI
- **Testing:** pytest with coverage
- **Linting:** ruff
- **Type Checking:** mypy
- **Formatting:** black + ruff

## Specialized Agents
- **TestAgent** (`prompts/agents/test-agent.yaml`): Comprehensive test generation
- **SecurityAgent** (`prompts/agents/security-agent.yaml`): Security review & threat modeling
- **RefactorAgent** (`prompts/agents/refactor-agent.yaml`): Code quality improvements
- **DocumentationAgent** (`prompts/agents/documentation-agent.yaml`): API & architecture documentation

## Mandatory Rules
1. **MUST** use TodoWrite to track all tasks and mark them complete
2. **MUST** delegate test generation to TestAgent
3. **MUST** delegate security review to SecurityAgent
4. **MUST** pass all quality checks (format, lint, type-check, test)
5. **MUST** address High/Critical security findings
6. **MUST** follow hexagonal architecture patterns
7. **MUST** maintain or improve code coverage
8. **MUST** create feature branch targeting release branch from VERSION

## Error Handling
If any step fails:
1. Mark the todo as still in_progress (not complete)
2. Analyze the failure
3. Fix the issue
4. Retry from the failed step
5. Do not skip steps or mark incomplete work as done

Start by reading the VERSION file and creating your TodoWrite implementation plan.
