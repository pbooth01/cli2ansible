# Claude Code Agent Prompts

This directory contains structured prompts and agent definitions for use with Claude Code to automate common development tasks.

## Quick Start

### Using an agent in Claude Code

```text
Load prompts/agents/test-agent.yaml
Input: <paste your git diff or file list>
```

### Available Agents

See [registry.yaml](registry.yaml) for the complete list.

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **TestAgent** | Generate and extend tests | Adding new features, fixing bugs, improving coverage |
| **SecurityAgent** | Security code review | Changes to auth, secrets, network, data handling |
| **RefactorAgent** | Code refactoring suggestions | Improving code structure, reducing complexity |
| **DocumentationAgent** | Generate/update docs | New features, API changes, architecture decisions |

## Directory Structure

```
prompts/
├── README.md              # This file
├── registry.yaml          # Index of all agents and snippets
├── agents/                # Agent definitions
│   ├── test-agent.yaml
│   ├── security-agent.yaml
│   ├── refactor-agent.yaml
│   └── documentation-agent.yaml
└── snippets/              # Reusable prompt snippets
    ├── unit-test-harness.md
    ├── threat-model-checklist.md
    └── api-documentation-template.md
```

## Agent Format

Each agent is defined in YAML with:

- **name**: Agent identifier
- **role**: High-level description of agent's purpose
- **inputs**: What the agent needs from you
- **policies**: Rules and constraints the agent follows
- **checklist**: Step-by-step process the agent executes
- **outputs**: Expected format and structure of results
- **style**: Tone and presentation preferences

## Example Usage

### Generate Tests for a Feature

```text
Load prompts/agents/test-agent.yaml

Input:
- diff: <paste git diff of your changes>
- codebase_map: src/cli2ansible/domain/services.py owns CompilePlaybook

Generate a test plan and test files for the changes.
```

### Security Review a PR

```text
Load prompts/agents/security-agent.yaml

Context:
- Auth: Bearer tokens in Authorization header
- Data: Session metadata may contain user input
- External calls: S3/MinIO for artifact storage

Input:
- diff: <paste git diff>

Perform security review and identify risks.
```

### Refactor Complex Code

```text
Load prompts/agents/refactor-agent.yaml

Input: src/cli2ansible/adapters/outbound/translator/rules_engine.py

The file has grown to 300+ lines. Suggest refactoring to improve maintainability.
```

## Integration with CI/CD

Agents can be invoked in CI pipelines:

```yaml
# .github/workflows/agents.yaml
- name: Security Review
  run: |
    python scripts/run_agent.py security-agent \
      --diff "${{ github.event.pull_request.diff_url }}"
```

## Creating Custom Agents

1. Copy an existing agent YAML as a template
2. Customize the role, inputs, policies, and checklist
3. Register it in `registry.yaml`
4. Test with sample inputs in Claude Code
5. Document usage examples in this README

## Best Practices

### For Users

- **Be specific**: Provide clear context and constraints
- **Iterate**: Start with broad questions, then drill down
- **Validate**: Always review agent output before applying
- **Feedback loop**: Update agent prompts based on results

### For Agent Designers

- **Clear role**: Define exactly what the agent should/shouldn't do
- **Concrete outputs**: Specify format, structure, and examples
- **Quality gates**: Include checklists to ensure consistency
- **Low noise**: Focus on high-signal, actionable results

## Tips

- Use agents early in development (design phase)
- Combine agents: Security review → Refactor → Test
- Keep diff sizes reasonable (<500 lines for best results)
- Provide domain context (auth model, data flow, etc.)
- Reference conventions docs for consistency

## Troubleshooting

**Agent doesn't understand my code:**
- Provide more context about the codebase structure
- Reference related files or modules
- Explain domain-specific concepts

**Output is too verbose:**
- Ask for "concise format only"
- Request specific sections only
- Update agent's style preferences

**Agent misses important issues:**
- Review the agent's checklist
- Add missing scenarios to policies
- Provide examples of expected behavior

## Contributing

To improve agents:

1. Test with real examples
2. Document edge cases or failures
3. Propose checklist updates
4. Share successful prompts with the team
