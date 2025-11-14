# Documentation Rules

## Overview
These rules ensure code is properly documented and maintainable.

## Rules

### 1. Docstrings Required
- **Severity**: Warning
- **Description**: All public functions and classes must have docstrings
- **Requirements**:
  - Use Google-style docstrings
  - Document parameters and return values
  - Include examples for complex functions
  - Explain purpose, not implementation

**Example**:
```python
def compile_playbook(session: Session) -> Report:
    """Compile shell commands into an Ansible playbook.

    Takes a session containing shell commands and generates an equivalent
    Ansible playbook with proper task structure and error handling.

    Args:
        session: Session containing commands to compile

    Returns:
        Report containing the generated playbook and metadata

    Raises:
        ValueError: If session has no commands

    Example:
        >>> session = Session(id=uuid4(), name="deploy", commands=["ls", "pwd"])
        >>> report = compile_playbook(session)
        >>> print(report.playbook_yaml)
    """
    ...
```

### 2. README Updates
- **Severity**: Warning
- **Description**: Update README when adding features or changing behavior
- **Update README for**:
  - New features or capabilities
  - Changed API endpoints
  - New configuration options
  - Installation changes
  - Breaking changes

### 3. API Documentation
- **Severity**: Warning
- **Description**: Document all HTTP endpoints
- **Requirements**:
  - Use FastAPI's automatic docs
  - Add descriptions to endpoints
  - Document request/response models
  - Include example requests
  - Document error responses

**Example**:
```python
@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
    description="""
    Create a new session with shell commands to be compiled into an Ansible playbook.

    The session will be persisted and can be retrieved later for compilation.
    """,
    responses={
        201: {"description": "Session created successfully"},
        400: {"description": "Invalid request data"},
        500: {"description": "Internal server error"}
    }
)
async def create_session(
    request: CreateSessionRequest,
    session_repo: SessionRepositoryPort = Depends(get_session_repository)
) -> SessionResponse:
    """Create a new session endpoint."""
    ...
```

### 4. Comments for Complex Logic
- **Severity**: Warning
- **Description**: Explain complex or non-obvious code
- **When to comment**:
  - Complex algorithms
  - Business rules
  - Workarounds or hacks
  - Performance optimizations
  - Security considerations

**Guidelines**:
- Explain **why**, not **what**
- Keep comments up to date
- Don't comment obvious code
- Use TODO/FIXME/NOTE markers

**Example**:
```python
# Calculate confidence based on command complexity and success rate
# Lower confidence for commands with pipes, redirects, or sudo
# NOTE: This heuristic may need tuning based on real-world usage
confidence = base_confidence * complexity_factor * success_rate
```

### 5. Type Documentation
- **Severity**: Warning
- **Description**: Document complex types and data structures
- **Requirements**:
  - Document dataclass fields
  - Explain enum values
  - Document type aliases
  - Add examples for complex types

**Example**:
```python
@dataclass
class Report:
    """Compilation report containing playbook and metadata.

    Attributes:
        id: Unique identifier for the report
        session_id: ID of the session that was compiled
        playbook_yaml: Generated Ansible playbook in YAML format
        success: Whether compilation succeeded
        errors: List of compilation errors, if any
        module_breakdown: Count of Ansible modules used
        confidence_high: Percentage of high-confidence conversions
        confidence_medium: Percentage of medium-confidence conversions
        confidence_low: Percentage of low-confidence conversions
    """
    id: UUID
    session_id: UUID
    playbook_yaml: str
    success: bool
    errors: list[str]
    module_breakdown: dict[str, int]
    confidence_high: float
    confidence_medium: float
    confidence_low: float
```

### 6. Changelog Maintenance
- **Severity**: Warning
- **Description**: Update CHANGELOG.md for notable changes
- **Include in changelog**:
  - New features
  - Bug fixes
  - Breaking changes
  - Deprecations
  - Security fixes

**Format**:
```markdown
## [Unreleased]

### Added
- New endpoint for batch session creation

### Changed
- Improved playbook compilation performance by 30%

### Fixed
- Fixed bug in command parsing for complex pipes

### Security
- Added input validation for file paths
```

## Documentation Types

### Code Documentation
- Docstrings for public APIs
- Inline comments for complex logic
- Type hints for all functions

### API Documentation
- OpenAPI/Swagger docs (auto-generated)
- Endpoint descriptions
- Request/response examples

### User Documentation
- README.md for getting started
- docs/ folder for detailed guides
- Architecture documentation

### Developer Documentation
- Contributing guidelines
- Architecture decisions (ADRs)
- Setup and development guides

## Enforcement
- Missing docstrings generate warnings
- API changes require documentation updates
- Complex code without comments may be rejected
- Documentation is reviewed as part of PR process
