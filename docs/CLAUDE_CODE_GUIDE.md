# Claude Code Integration Guide

This project is optimized for use with Claude Code, featuring structured agents, coding conventions, and automation helpers.

## 🚀 Quick Start with Claude Code

### 1. Load Project Context

When starting a new Claude Code session:

```text
Load .claude/context.json
```

This gives Claude understanding of:
- Project architecture (hexagonal)
- Tech stack (FastAPI, PostgreSQL, Poetry)
- Key files and conventions
- Common tasks and commands

### 2. Use Agents for Common Tasks

#### Generate Tests

```text
Load prompts/agents/test-agent.yaml

Input:
- diff: <paste git diff>

Generate test plan and test files for my changes.
```

#### Security Review

```text
Load prompts/agents/security-agent.yaml

Context:
- Auth: Currently none (future: Bearer tokens)
- Data: Terminal recordings may contain secrets

Input:
- diff: <paste git diff>

Perform security review.
```

#### Refactor Code

```text
Load prompts/agents/refactor-agent.yaml

Input: src/cli2ansible/adapters/outbound/translator/rules_engine.py

The file has grown large. Suggest refactorings.
```

#### Generate Documentation

```text
Load prompts/agents/documentation-agent.yaml

Scope: Document the CompilePlaybook service
Audience: developers

Generate documentation with examples.
```

## 📚 Available Resources

### Conventions

- **[CODE_STYLE.md](conventions/CODE_STYLE.md)** - General coding principles
- **[python.md](conventions/python.md)** - Python-specific conventions
- **[backend_api.md](conventions/backend_api.md)** - API design guidelines

### Agents

- **[test-agent.yaml](../prompts/agents/test-agent.yaml)** - Test generation
- **[security-agent.yaml](../prompts/agents/security-agent.yaml)** - Security review
- **[refactor-agent.yaml](../prompts/agents/refactor-agent.yaml)** - Code refactoring
- **[documentation-agent.yaml](../prompts/agents/documentation-agent.yaml)** - Documentation generation

### Templates

- **[PRD Template](prds/TEMPLATE.md)** - Feature requirements document
- **[ADR Template](decisions/ADR-TEMPLATE.md)** - Architecture decision record

### Snippets

- **[unit-test-harness.md](../prompts/snippets/unit-test-harness.md)** - Testing patterns
- **[threat-model-checklist.md](../prompts/snippets/threat-model-checklist.md)** - Security checklist

## 🔄 Development Workflows

### Feature Development Workflow

1. **Plan** (optional)
   ```text
   Load docs/prds/TEMPLATE.md
   Help me create a PRD for: <feature description>
   ```

2. **Design**
   ```text
   Load .claude/context.json
   I want to add: <feature>
   Suggest an implementation approach following hexagonal architecture.
   ```

3. **Implement**
   - Write code following conventions in [docs/conventions/](conventions/)
   - Reference domain models in [src/cli2ansible/domain/](../src/cli2ansible/domain/)

4. **Test**
   ```text
   Load prompts/agents/test-agent.yaml
   Input: <git diff>
   Generate tests.
   ```

5. **Review**
   ```text
   Load prompts/agents/security-agent.yaml
   Input: <git diff>
   Perform security review.
   ```

6. **Document**
   ```text
   Load prompts/agents/documentation-agent.yaml
   Scope: <what changed>
   Generate documentation.
   ```

### Bug Fix Workflow

1. **Understand**
   ```text
   Load .claude/context.json
   Help me understand this bug: <description>
   Where should I look in the codebase?
   ```

2. **Fix**
   - Implement fix following conventions
   - Add regression test

3. **Test**
   ```text
   Load prompts/agents/test-agent.yaml
   Input: <git diff>
   Generate tests including regression test for the bug.
   ```

### Refactoring Workflow

1. **Analyze**
   ```text
   Load prompts/agents/refactor-agent.yaml
   Input: <file path>
   Metrics:
     - Lines: <count>
     - Complexity: <score>
   Suggest refactorings.
   ```

2. **Refactor**
   - Implement suggested changes
   - Ensure tests still pass

3. **Verify**
   ```bash
   make test
   make lint
   ```

## 💡 Pro Tips

### Get File-Specific Help

```text
Load .claude/context.json
Read src/cli2ansible/domain/services.py

Explain how CompilePlaybook works and suggest improvements.
```

### Understand Architecture

```text
Load .claude/context.json
Load docs/conventions/CODE_STYLE.md

Explain the hexagonal architecture of this project with examples.
```

### Debug Issues

```text
Load .claude/context.json

I'm getting this error: <error message>

Help me debug this. What should I check?
```

### Write Better Code

```text
Load docs/conventions/python.md

Review this code for convention violations:
<paste code>
```

### Plan Architecture Changes

```text
Load .claude/context.json

I need to add real-time session monitoring. Suggest an architecture that:
- Maintains hexagonal structure
- Doesn't break existing APIs
- Scales well
```

## 🤖 Agent Best Practices

### Provide Context

Good:
```text
Load prompts/agents/security-agent.yaml

Context:
- Auth: Bearer tokens
- Data: User sessions contain PII
- External: S3 for artifacts

Input: <diff>
```

Better than:
```text
Load prompts/agents/security-agent.yaml
Input: <diff>
```

### Be Specific

Good:
```text
Load prompts/agents/test-agent.yaml

Input: <diff of new translation rule>

Generate unit tests for the new rule, including:
- Happy path
- Edge cases (missing args, malformed input)
- Integration with existing rules
```

Better than:
```text
Generate tests for my changes.
```

### Iterate

1. Start broad: "Suggest test strategy"
2. Then specific: "Generate tests for X"
3. Then refine: "Add edge case for Y"

## 📦 Common Tasks

### Start a New Feature

```bash
# 1. Create PRD
cp docs/prds/TEMPLATE.md docs/prds/2025-11-04-feature-name.md

# 2. Get Claude's help
Load docs/prds/2025-11-04-feature-name.md
Load .claude/context.json

Help me fill out this PRD for: <feature description>

# 3. Implement with Claude's guidance
Load .claude/context.json
I'm implementing: <feature>
Suggest the implementation approach.

# 4. Generate tests
Load prompts/agents/test-agent.yaml
<generate tests>

# 5. Review security
Load prompts/agents/security-agent.yaml
<security review>
```

### Add a Translation Rule

```text
Load .claude/context.json
Read src/cli2ansible/adapters/outbound/translator/rules_engine.py

I want to add support for: docker run commands

Suggest:
1. Where to add the rule
2. Regex pattern to match
3. Ansible module to use
4. Test cases
```

### Improve Test Coverage

```text
Load .claude/context.json
Load prompts/snippets/unit-test-harness.md

Current coverage: 75%
Target: 90%

Identify untested code paths in:
src/cli2ansible/domain/services.py

Suggest tests to add.
```

### Document a Module

```text
Load prompts/agents/documentation-agent.yaml

Scope: src/cli2ansible/adapters/outbound/translator/
Audience: developers

Generate developer documentation explaining:
- How translation works
- How to add new rules
- Examples
```

## 🔧 Customizing Agents

### Modify an Agent

1. Open agent YAML file (e.g., `prompts/agents/test-agent.yaml`)
2. Update sections:
   - `role`: Agent's purpose
   - `policies`: Rules to follow
   - `checklist`: Steps to execute
   - `style`: Output preferences
3. Test with sample input
4. Update `prompts/registry.yaml` if needed

### Create a New Agent

1. Copy existing agent as template
2. Customize for your use case
3. Add to `prompts/registry.yaml`
4. Document usage in `prompts/README.md`
5. Test and iterate

## 📖 Learning Resources

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[README.md](../README.md)** - Project overview
- **[Conventions](conventions/)** - Coding standards
- **[Prompts](../prompts/)** - Agent definitions

## 🆘 Troubleshooting

### Agent Not Giving Expected Output

1. Check agent YAML for clarity
2. Provide more context
3. Be more specific in request
4. Break into smaller steps

### Context Not Loading

1. Verify file path is correct
2. Check JSON syntax (for .claude/context.json)
3. Try loading individual files
4. Refresh Claude Code session

### Generated Code Doesn't Match Style

1. Reference conventions explicitly:
   ```text
   Load docs/conventions/python.md
   Follow these conventions: <paste code to fix>
   ```

2. Ask for style review:
   ```text
   Load docs/conventions/CODE_STYLE.md
   Review this code for style violations: <code>
   ```

## 🎯 Next Steps

1. **Familiarize** with agents - try each one
2. **Customize** agents for your workflow
3. **Create** new snippets for common patterns
4. **Share** useful prompts with the team
5. **Iterate** - improve agents based on experience

---

Happy coding with Claude! 🚀
