# Security Rules

## Overview
These rules prevent common security vulnerabilities and ensure secure coding practices.

## Rules

### 1. No Hardcoded Secrets
- **Severity**: Critical
- **Description**: Never commit secrets, credentials, or sensitive data
- **Check for**:
  - API keys, tokens, passwords in code
  - Database credentials
  - Private keys or certificates
  - AWS/cloud credentials
  - Webhook URLs with tokens

**Example - Bad**:
```python
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"
```

**Example - Good**:
```python
import os
API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
```

### 2. Input Validation
- **Severity**: Critical
- **Description**: All user input must be validated at API boundaries
- **Requirements**:
  - Validate all HTTP request parameters
  - Use Pydantic models for request validation
  - Sanitize file paths
  - Validate file uploads (type, size)
  - Check data types and ranges

**Example**:
```python
class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    commands: list[str] = Field(..., min_items=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

### 3. SQL Injection Prevention
- **Severity**: Critical
- **Description**: Always use parameterized queries
- **Requirements**:
  - Use SQLAlchemy ORM or parameterized queries
  - Never concatenate user input into SQL
  - Use query builders, not raw SQL strings

**Example - Bad**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Example - Good**:
```python
query = select(User).where(User.id == user_id)
```

### 4. Command Injection Prevention
- **Severity**: Critical
- **Description**: Never execute shell commands with unsanitized input
- **Requirements**:
  - Avoid `os.system()`, `subprocess.shell=True`
  - Use subprocess with argument lists
  - Validate and sanitize command arguments
  - Use allowlists for permitted commands

**Example - Bad**:
```python
os.system(f"ls {user_path}")
```

**Example - Good**:
```python
import subprocess
subprocess.run(["ls", user_path], check=True, capture_output=True)
```

### 5. Path Traversal Prevention
- **Severity**: Critical
- **Description**: Prevent directory traversal attacks
- **Requirements**:
  - Validate file paths
  - Use `pathlib.Path.resolve()` to normalize paths
  - Check paths are within allowed directories
  - Never trust user-supplied paths directly

**Example**:
```python
from pathlib import Path

def safe_read_file(filename: str, base_dir: Path) -> str:
    file_path = (base_dir / filename).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Path traversal detected")
    return file_path.read_text()
```

### 6. Proper Authentication & Authorization
- **Severity**: Critical
- **Description**: Verify user identity and permissions
- **Requirements**:
  - Authenticate all protected endpoints
  - Check authorization before operations
  - Use secure session management
  - Implement proper RBAC if needed
  - Don't trust client-side data

## Additional Security Checks

### 7. Secure Dependencies
- Check for known vulnerabilities in dependencies
- Keep dependencies up to date
- Use `pip-audit` or similar tools

### 8. Logging Security
- Don't log sensitive data (passwords, tokens, PII)
- Sanitize logs before writing
- Use appropriate log levels

### 9. Error Messages
- Don't expose internal details in error messages
- Use generic messages for authentication failures
- Log detailed errors server-side only

## Enforcement
- Security violations are **CRITICAL** and block merge
- All security issues must be fixed before approval
- Security reviews are mandatory for all PRs
