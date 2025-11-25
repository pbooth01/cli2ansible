# Refactoring Opportunity: DatabaseHelper Logging

## Overview
This branch contains code that demonstrates a common refactoring scenario: converting print-based logging to proper structured logging using Python's `logging` module.

## Current State (Before Refactoring)

### Problem
The `DatabaseHelper` class (`src/cli2ansible/adapters/outbound/db/db_helper.py`) uses `print()` statements for logging database operations:

```python
def log_query(self, operation: str, table: str, details: str = "") -> None:
    if self.verbose:
        message = f"[DB] {operation} on {table}"
        if details:
            message += f" - {details}"
        print(message)  # ❌ Using print instead of proper logging

def log_error(self, operation: str, error: Exception) -> None:
    print(f"[DB ERROR] {operation} failed: {str(error)}", file=sys.stderr)  # ❌
```

### Issues with Current Approach
1. **No log levels**: Can't control verbosity (DEBUG, INFO, WARNING, ERROR)
2. **No log formatting**: Can't customize output format
3. **No log handlers**: Can't redirect to files, syslog, or monitoring systems
4. **Hard to test**: Print statements are difficult to capture in unit tests
5. **Not production-ready**: Can't integrate with logging infrastructure
6. **No context**: Missing timestamps, module names, line numbers

### Where It's Used
The `DatabaseHelper` is currently used in 3 repository classes:
- `SQLAlchemySessionRepo` (session CRUD operations)
- `SQLAlchemyCommandRepo` (command storage)
- `SQLAlchemyEventRepo` (event storage)

## Proposed Refactoring

### Goal
Replace all `print()` statements with Python's standard `logging` module.

### Benefits
1. ✅ **Configurable log levels**: Control verbosity per environment
2. ✅ **Structured logging**: Add context (timestamps, module, function)
3. ✅ **Multiple handlers**: Log to console, files, or external services
4. ✅ **Production-ready**: Integrates with standard logging infrastructure
5. ✅ **Testable**: Easy to capture and assert on log messages
6. ✅ **Performance**: Can disable logging without code changes

### Example Refactored Code

**Before:**
```python
def log_query(self, operation: str, table: str, details: str = "") -> None:
    if self.verbose:
        message = f"[DB] {operation} on {table}"
        if details:
            message += f" - {details}"
        print(message)
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

def log_query(self, operation: str, table: str, details: str = "") -> None:
    logger.debug(
        "Database query: %s on %s",
        operation,
        table,
        extra={"details": details, "table": table, "operation": operation}
    )
```

## Refactoring Steps

1. **Add logging configuration**
   - Create or update logging configuration
   - Set appropriate log levels per environment

2. **Update DatabaseHelper class**
   - Import `logging` module
   - Create logger instance
   - Replace all `print()` with appropriate `logger.*()` calls
   - Map operations to log levels (DEBUG, INFO, WARNING, ERROR)

3. **Remove verbose flag**
   - Let logging configuration control verbosity
   - Remove `self.verbose` checks

4. **Update tests**
   - Use `caplog` fixture to test logging
   - Assert on log messages and levels

5. **Add structured logging**
   - Use `extra` parameter for context
   - Consider JSON logging for production

## Testing the Refactoring

Run the existing test suite to ensure no functionality breaks:
```bash
make test-unit
```

All 101 tests should pass before and after refactoring.

## Files to Modify

1. `src/cli2ansible/adapters/outbound/db/db_helper.py` - Main refactoring target
2. `src/cli2ansible/adapters/outbound/db/sqlalchemy_session_repo.py` - Uses DatabaseHelper
3. `src/cli2ansible/adapters/outbound/db/sqlalchemy_command_repo.py` - Uses DatabaseHelper
4. `src/cli2ansible/adapters/outbound/db/sqlalchemy_event_repo.py` - Uses DatabaseHelper
5. `tests/unit/test_db_helper.py` - New test file for DatabaseHelper (optional)

## Success Criteria

- ✅ No `print()` statements in DatabaseHelper
- ✅ All logging uses Python's `logging` module
- ✅ Log levels are appropriate (DEBUG for queries, ERROR for errors)
- ✅ All existing tests pass
- ✅ Logging can be configured via environment or config file
- ✅ No breaking changes to repository classes

## Additional Improvements (Optional)

1. Add correlation IDs for request tracing
2. Add performance metrics (query duration)
3. Implement log sampling for high-volume operations
4. Add structured logging with JSON formatter
5. Integrate with observability tools (DataDog, New Relic, etc.)

---

**Branch:** `feature/augment-agent-refactor-demo`  
**Commit:** See latest commit for the "before" state  
**Next Step:** Refactor DatabaseHelper to use proper logging

