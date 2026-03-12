---
name: spec-driven-dev
description: Implement new features using a structured spec-driven development workflow with planning, implementation, testing, and security scanning phases
---

# Spec-Driven Development Command

This command implements a structured workflow for developing new features. It ensures that all new features go through proper planning, specification review, implementation, testing, and security scanning phases.

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. PLANNING PHASE                                                          │
│     └── Planning Agent writes detailed spec in SDD/ directory              │
│                              ▼                                              │
│  2. REVIEW PHASE (USER)                                                     │
│     └── User reviews and approves the spec                                  │
│                              ▼                                              │
│  3. IMPLEMENTATION PHASE                                                    │
│     └── Code Implementation Agent implements the spec                       │
│                              ▼                                              │
│  4. TESTING PHASE                                                           │
│     └── Unit Test Agent writes tests for the implementation                 │
│                              ▼                                              │
│  5. SECURITY PHASE                                                          │
│     └── Security Agent scans for vulnerabilities                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How to Use

Invoke this command with a description of the feature you want to implement:

```
/spec-driven-dev <feature description>
```

### Example

```
/spec-driven-dev Add a caching layer for the API using Redis to improve response times
```

## Phase Details

### Phase 1: Planning (Automatic)

The **planning-agent** will:

1. Analyze the codebase to understand existing patterns
2. Create a detailed Software Design Document (SDD) in the `SDD/` directory
3. The SDD will be named: `SDD/{TICKET-ID}-{Feature-Name}.md` (or auto-generated name if no ticket)
4. Include:
   - Problem statement and objectives
   - Current state analysis
   - Proposed architecture with diagrams
   - Detailed design with code examples
   - Implementation plan with specific file paths
   - Configuration requirements
   - Testing strategy

### Phase 2: User Review (Manual)

After the spec is generated, **YOU** must:

1. Review the SDD document in the `SDD/` directory
2. Verify the proposed approach meets your requirements
3. Request changes if needed
4. **Explicitly approve** the spec to proceed (say "approved" or "proceed")

⚠️ **The workflow will WAIT for your approval before proceeding to implementation.**

### Phase 3: Implementation (Automatic)

Once approved, the **implementation-agent** will:

1. Read the approved SDD document
2. Create new files at the specified paths
3. Modify existing files as described
4. Add any required dependencies
5. Follow existing codebase patterns and conventions

### Phase 4: Testing (Automatic)

The **testing-agent** will:

1. Analyze the implemented code
2. Write comprehensive unit tests covering:
   - Happy path scenarios
   - Edge cases and boundary conditions
   - Error handling
3. Place tests in the appropriate test directories
4. Follow existing test patterns in the codebase

### Phase 5: Security Scanning (Automatic)

The **security-agent** will:

1. Run Snyk code analysis (SAST) on the new code
2. Scan for vulnerable dependencies (SCA)
3. Check for security misconfigurations
4. Provide a security report with:
   - Vulnerabilities found by severity
   - Remediation recommendations
   - Pass/fail status

## SDD Document Template

The planning agent will create SDDs following this structure:

```markdown
# {Feature Name} - Software Design Document

## 1. Overview
- Problem statement
- Objectives
- Scope

## 2. Current State Analysis
- Existing relevant code
- Integration points
- Dependencies

## 3. Proposed Architecture
- High-level design
- Data flow diagrams
- Component interactions

## 4. Detailed Design
- New classes/modules with code examples
- Modified files with change descriptions
- API specifications

## 5. Implementation Plan
### 5.1 Tasks (prioritized)
### 5.2 New Files to Create
### 5.3 Files to Modify
### 5.4 Dependencies to Add

## 6. Configuration Requirements
- Environment variables
- Config file changes

## 7. Testing Strategy
- Unit tests to write
- Integration tests needed
- Test data requirements

## 8. Security Considerations
- Authentication/authorization
- Input validation
- Data protection
```

## Interrupting the Workflow

You can interrupt the workflow at any point by:
- Requesting changes to the spec during review
- Asking for modifications during implementation
- Requesting additional tests
- Asking for security fixes before proceeding

## Best Practices

1. **Be specific** in your feature description for better specs
2. **Review specs carefully** - implementation follows the spec exactly
3. **Request changes early** - easier to modify specs than implementations
4. **Don't skip security** - always complete the security scan phase

## Agent References

This command uses the following agents from `.augment/agents/`:

- `planning-agent.md` - Creates the SDD specification
- `implementation-agent.md` - Implements the approved spec
- `testing-agent.md` - Writes unit tests for the implementation
- `security-agent.md` - Scans for security vulnerabilities

