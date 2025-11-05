# Code Style (General)

## Principles

- **Hexagonal Architecture**: Keep domain logic pure; adapters handle I/O
- **Small, cohesive modules**: Each module should have a single, well-defined purpose
- **Explicit over implicit**: Type hints, clear naming, no magic
- **Fail fast**: Validate inputs at boundaries; raise meaningful exceptions
- **Testability first**: Design for testing; inject dependencies

## Documentation

- All public functions/classes must have docstrings
- Include usage examples for non-trivial APIs
- Document WHY, not just WHAT (code shows what)

## Logging & Observability

- Use structured logging (structlog)
- Include trace context (session_id, user_id, etc.)
- **NEVER** log secrets, tokens, or PII
- Log at appropriate levels:
  - ERROR: Requires immediate action
  - WARNING: Unexpected but handled
  - INFO: Key business events
  - DEBUG: Diagnostic details

## Error Handling

- Use domain-specific exceptions
- Never swallow exceptions silently
- Provide actionable error messages
- Include context (what failed, why, how to fix)

## Dependencies

- Pin versions in production
- Keep dependencies minimal
- Review security advisories regularly
- Document why each dependency is needed

## Code Review

- Every change requires review
- CI must pass (tests + lint + type-check)
- Security review for auth/secrets/network changes
- Test coverage should not decrease
