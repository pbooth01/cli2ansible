# Refactoring Demo: Print Statements to Structured Logging

## Overview
This branch demonstrates a realistic refactoring scenario: converting print-based logging to proper structured logging using Python's `logging` module across multiple layers of a hexagonal architecture application.

## Current State (Anti-Pattern)

### Problem
The codebase uses `print()` statements for logging across **two architectural layers**:

1. **Data Layer (Repository Pattern)** - 3 files
2. **Application Layer (Use Cases)** - 1 file

This violates the code quality rule defined in `.augment/rules/code-quality.md`:
> **Rule #6: Use Structured Logging, Not Print Statements**

### Files with Print Statements

#### Data Layer (`src/cli2ansible/adapters/outbound/db/`)
1. **`sqlalchemy_session_repo.py`** (87 lines)
   - Session CRUD operations
   - Print statements in: `create()`, `get()`, `delete()`
   - Example: `print(f"[DB TRANSACTION] Starting: Creating session {session.id}")`

2. **`sqlalchemy_command_repo.py`** (42 lines)
   - Command storage operations
   - Print statements in: `save_commands()`, `get_commands()`
   - Example: `print(f"[DB] INSERT on commands - count={len(commands)}")`

3. **`sqlalchemy_event_repo.py`** (54 lines)
   - Event storage operations
   - Print statements in: `save_events()`
   - Example: `print(f"[DB SUCCESS] Events saved ({len(events)} records)")`

#### Application Layer (`src/cli2ansible/application/`)
4. **`ingest.py`** (134 lines)
   - Session ingestion use cases
   - Print statements in: `create_session()`, `get_session()`, `list_sessions()`, `delete_session()`, `upload_cast_file()`, `save_events()`, `get_events()`
   - Example: `print(f"[INGEST] Creating new session: {req.name}")`

### Total Impact
- **4 files** with print statements
- **2 architectural layers** affected
- **~30+ print statements** across the codebase
- **Multiple operations**: CRUD, transactions, file uploads, error handling

## Why This Is Bad

1. ❌ **No log levels** - Can't filter by severity (DEBUG, INFO, WARNING, ERROR)
2. ❌ **No configuration** - Can't control verbosity per environment
3. ❌ **No handlers** - Can't redirect to files, syslog, or monitoring systems
4. ❌ **Hard to test** - Print statements are difficult to capture and assert
5. ❌ **Not production-ready** - Can't integrate with logging infrastructure
6. ❌ **Missing context** - No timestamps, module names, line numbers, or correlation IDs
7. ❌ **Performance** - Can't disable logging without code changes

## Refactoring Goal

Convert all `print()` statements to Python's standard `logging` module with:
- ✅ Appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Structured logging with context
- ✅ Configurable per environment
- ✅ Production-ready
- ✅ Testable

## Example Refactoring

### Before (Current)
```python
def create_session(self, req: SessionCreateRequestDTO) -> SessionResponseDTO:
    """Create a new session."""
    print(f"[INGEST] Creating new session: {req.name}")
    session = Session(name=req.name, metadata=req.metadata or {})
    created = self.repo.create(session)
    print(f"[INGEST] Session created successfully: {created.id}")
    return self._session_to_response(created)
```

### After (Target)
```python
import logging

logger = logging.getLogger(__name__)

def create_session(self, req: SessionCreateRequestDTO) -> SessionResponseDTO:
    """Create a new session."""
    logger.info("Creating new session", extra={"session_name": req.name})
    session = Session(name=req.name, metadata=req.metadata or {})
    created = self.repo.create(session)
    logger.info("Session created successfully", extra={"session_id": str(created.id), "session_name": created.name})
    return self._session_to_response(created)
```

## Refactoring Steps

### 1. Add Logging Configuration
Create or update logging configuration in the application startup.

### 2. Update Data Layer Files
- `sqlalchemy_session_repo.py`
- `sqlalchemy_command_repo.py`
- `sqlalchemy_event_repo.py`

Replace print statements with appropriate logger calls:
- `print(f"[DB] ...")` → `logger.debug(...)`
- `print(f"[DB SUCCESS] ...")` → `logger.info(...)`
- `print(f"[DB ERROR] ...", file=sys.stderr)` → `logger.error(...)`

### 3. Update Application Layer Files
- `ingest.py`

Replace print statements with appropriate logger calls:
- `print(f"[INGEST] ...")` → `logger.info(...)`
- `print(f"[INGEST ERROR] ...")` → `logger.error(...)`

### 4. Add Structured Context
Use the `extra` parameter to add structured context:
```python
logger.info("Operation completed", extra={
    "session_id": str(session_id),
    "record_count": len(records),
    "operation": "save_events"
})
```

### 5. Update Tests
- Use `caplog` fixture to test logging
- Assert on log messages and levels
- Verify structured context

## Success Criteria

- ✅ No `print()` statements in the 4 affected files
- ✅ All logging uses Python's `logging` module
- ✅ Log levels are appropriate for each operation
- ✅ All existing tests pass (101 tests)
- ✅ Logging can be configured via environment or config file
- ✅ No breaking changes to public APIs

## Testing

Run the test suite to ensure no functionality breaks:
```bash
make test-unit
```

Expected: All 101 tests should pass before and after refactoring.

## Branch Information

- **Branch:** `feature/augment-agent-refactor-demo`
- **Base:** `main`
- **Status:** Ready for refactoring demonstration
- **Tests:** ✅ 101 passing
- **Coverage:** 77%

---

**Next Step:** Use Augment Code to refactor these print statements to proper structured logging!

