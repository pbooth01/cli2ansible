---
type: "always_apply"
---

# Code Quality Rules

## Overview
These rules ensure code quality, maintainability, and adherence to project conventions.

## Rules

### 1. Follow Project Coding Conventions
- **Severity**: Warning
- **Description**: All code must follow the project coding conventions
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

### 6. Use Structured Logging, Not Print Statements
- **Severity**: Warning
- **Description**: Never use `print()` for logging; use Python's `logging` module
- **Requirements**:
  - Use `logging` module for all application logging
  - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Include context in log messages
  - Configure logging centrally, not in individual modules
  - Use structured logging with extra fields for production systems

**Example - Bad**:
```python
def process_data(data: dict) -> None:
    print(f"Processing data: {data}")  # ❌ Don't use print
    try:
        result = transform(data)
        print(f"Success: {result}")  # ❌ No log levels
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # ❌ Not structured
```

**Example - Good**:
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict) -> None:
    logger.debug("Processing data", extra={"data_keys": list(data.keys())})
    try:
        result = transform(data)
        logger.info("Data processed successfully", extra={"result_count": len(result)})
    except Exception as e:
        logger.error("Failed to process data", exc_info=True, extra={"data_id": data.get("id")})
        raise
```

**Rationale**:
- Print statements cannot be controlled or configured
- No log levels means no way to filter by severity
- Cannot redirect to files, monitoring systems, or log aggregators
- Difficult to test and validate
- Not suitable for production environments
- Missing context like timestamps, module names, and line numbers
