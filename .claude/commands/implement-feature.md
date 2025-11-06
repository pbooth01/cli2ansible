---
description: Generate PRD (if needed), implement feature, run tests, security review, and create PR
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), Glob(*), Grep(*), Task(*), TodoWrite(*), WebFetch(*), WebSearch(*)
---

# Implement Feature

You are a feature implementation orchestrator for the cli2ansible project.

## Your Task
Generate and execute a complete workflow to implement a feature from PRD through to PR creation, using specialized agents and ensuring all quality checks pass.

## Context Setup
First, determine if a PRD exists:

**If user provides an EXPLICIT PRD path (e.g., "docs/prds/my-feature.md"):**
1. Read `VERSION` file to determine release branch (`release-<version>`)
2. Read the PRD content from the specified path
3. Load specialized agent definitions from `prompts/agents/`
4. Proceed to Step 1: Planning

**If user provides ONLY a feature description (no explicit PRD path):**
1. Read `VERSION` file to determine release branch (`release-<version>`)
2. Generate PRD using PRDAgent (see PRD Generation Workflow below)
3. Save the PRD to `docs/prds/<feature-name>.md`
4. **CRITICAL:** Present the generated PRD to the user for review
5. **WAIT for explicit user approval** before proceeding (user must reply "approved" or similar)
6. If user requests changes, update the PRD and ask for approval again
7. Only after approval: Load specialized agent definitions from `prompts/agents/`
8. Only after approval: Proceed to Step 1: Planning

### PRD Generation Workflow (when no PRD provided)

Use the Task tool with general-purpose agent:

```
Use Task tool with general-purpose agent:

"Read prompts/agents/prd-agent.yaml to understand PRDAgent's role and responsibilities.

Acting as PRDAgent, generate a comprehensive PRD for the following feature request:

<user's feature description>

Follow the PRDAgent checklist:
1. Analyze the codebase to understand existing patterns
   - Search for similar features or integrations
   - Review architecture (hexagonal pattern)
   - Identify affected components
2. Research dependencies and integration points
   - External APIs or services
   - Internal components that will change
3. Generate complete PRD following docs/prds/TEMPLATE.md
   - Include all required sections
   - Provide specific, testable requirements
   - Define clear success metrics
   - Identify risks and mitigations

Codebase context:
- Architecture: Hexagonal (ports & adapters)
- Tech stack: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- Testing: pytest with coverage requirements
- Key directories:
  - src/cli2ansible/domain/ (business logic)
  - src/cli2ansible/adapters/ (external integrations)
  - src/cli2ansible/domain/ports.py (interfaces)

Return the complete PRD in markdown format ready to save to docs/prds/<feature-name>.md"
```

After receiving the PRD from PRDAgent:
1. Save it to `docs/prds/<feature-name>.md`
2. Present the PRD contents to the user
3. Ask: "**PRD created at docs/prds/<feature-name>.md**. Please review the PRD above. Reply with 'approved' to proceed with implementation, or provide feedback for revisions."
4. **STOP and WAIT for user response - DO NOT PROCEED**
5. If user requests changes, update the PRD file and ask for approval again
6. Only proceed to implementation planning after explicit user approval ("approved", "looks good", "ok", etc.)

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
- **PRDAgent** (`prompts/agents/prd-agent.yaml`): PRD generation from feature requests
- **TestAgent** (`prompts/agents/test-agent.yaml`): Comprehensive test generation
- **SecurityAgent** (`prompts/agents/security-agent.yaml`): Security review & threat modeling
- **RefactorAgent** (`prompts/agents/refactor-agent.yaml`): Code quality improvements
- **DocumentationAgent** (`prompts/agents/documentation-agent.yaml`): API & architecture documentation

## Mandatory Rules
1. **MUST** generate PRD using PRDAgent if user doesn't provide an explicit PRD path
2. **MUST** save PRD to docs/prds/ directory before showing to user
3. **MUST** wait for explicit user approval of PRD before implementing (STOP and WAIT)
4. **MUST** use TodoWrite to track all tasks and mark them complete
5. **MUST** delegate test generation to TestAgent
6. **MUST** delegate security review to SecurityAgent
7. **MUST** pass all quality checks (format, lint, type-check, test)
8. **MUST** address High/Critical security findings
9. **MUST** follow hexagonal architecture patterns
10. **MUST** maintain or improve code coverage
11. **MUST** create feature branch targeting release branch from VERSION

## Error Handling
If any step fails:
1. Mark the todo as still in_progress (not complete)
2. Analyze the failure
3. Fix the issue
4. Retry from the failed step
5. Do not skip steps or mark incomplete work as done

## Getting Started

**Step 1:** Read the VERSION file to determine the target release branch.

**Step 2:** Determine if a PRD path was EXPLICITLY provided:
- **Explicit PRD path provided** (e.g., "implement docs/prds/my-feature.md"): Read the PRD and proceed to implementation.
- **NO explicit PRD path** (e.g., "implement support for X feature"):
  1. Use PRDAgent to generate a PRD
  2. Save to docs/prds/<feature-name>.md
  3. Show PRD to user for review
  4. **STOP and WAIT for user approval**
  5. Do not proceed until user explicitly approves

**Step 3:** After PRD is confirmed/approved, create a TodoWrite implementation plan and begin work.
