# Code Quality Rules

## Overview
These rules ensure code quality, maintainability, and adherence to project conventions.

## Rules

### 1. Follow Project Coding Conventions
- **Severity**: Warning
- **Description**: All code must follow the conventions defined in `docs/conventions/CODE_STYLE.md`
- **Check for**:
  - Consistent naming conventions (snake_case for functions/variables, PascalCase for classes)
  - Proper module organization
  - Import ordering (standard library, third-party, local)
  - Line length limits (max 100 characters)

### 2. No Code Smells
- **Severity**: Warning
- **Description**: Avoid common code smells and anti-patterns
- **Examples of violations**:
  - Long functions (>50 lines)
  - Too many parameters (>5)
  - Deeply nested code (>3 levels)
  - Duplicate code
  - Dead code or unused imports
  - Magic numbers without constants

### 3. Proper Error Handling
- **Severity**: Warning
- **Description**: All error cases must be handled appropriately
- **Requirements**:
  - Use specific exception types, not bare `except:`
  - Log errors with appropriate context
  - Raise custom exceptions for domain errors
  - Handle async errors properly
  - Don't silently swallow exceptions

**Example - Bad**:
```python
try:
    result = risky_operation()
except:
    pass
```

**Example - Good**:
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value in risky_operation: {e}")
    raise DomainError("Operation failed due to invalid input") from e
```

### 4. Clear Naming
- **Severity**: Warning
- **Description**: Names must be descriptive and follow conventions
- **Requirements**:
  - Variable names describe their purpose
  - Function names are verbs describing actions
  - Class names are nouns describing entities
  - Avoid abbreviations unless widely known
  - Boolean variables start with `is_`, `has_`, `can_`, etc.

### 5. Type Hints Required
- **Severity**: Warning
- **Description**: All functions must have type hints
- **Requirements**:
  - Function parameters have type hints
  - Return types are specified
  - Use `Optional[T]` for nullable values
  - Use `Union[T1, T2]` for multiple types
  - Complex types use proper generics

**Example**:
```python
def process_command(
    command: str,
    options: dict[str, Any],
    timeout: Optional[int] = None
) -> CommandResult:
    ...
```

### 6. No Unnecessary Complexity
- **Severity**: Warning
- **Description**: Keep code simple and readable
- **Avoid**:
  - Overly clever one-liners
  - Unnecessary abstractions
  - Premature optimization
  - Complex nested comprehensions
  - Multiple operations in one line

**Example - Bad**:
```python
result = [x for sublist in [y.split(',') for y in data if y] for x in sublist if x.strip()]
```

**Example - Good**:
```python
result = []
for line in data:
    if line:
        parts = line.split(',')
        result.extend(part.strip() for part in parts if part.strip())
```

## Enforcement
- These rules are checked on every PR
- Violations generate warnings in the review
- Multiple violations may block merge
