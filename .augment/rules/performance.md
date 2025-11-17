# Performance Rules

## Overview
These rules ensure efficient code and prevent common performance issues.

## Rules

### 1. No N+1 Query Problems
- **Severity**: Warning
- **Description**: Avoid executing queries in loops
- **Problem**: Loading related data in a loop causes N+1 queries

**Example - Bad**:
```python
# Loads sessions, then makes N queries for reports
sessions = session_repo.find_all()
for session in sessions:
    report = report_repo.find_by_session_id(session.id)  # N queries!
```

**Example - Good**:
```python
# Load all data with joins or eager loading
sessions_with_reports = session_repo.find_all_with_reports()  # 1 query
```

**SQLAlchemy Solution**:
```python
# Use joinedload or selectinload
from sqlalchemy.orm import joinedload

sessions = (
    db.query(SessionModel)
    .options(joinedload(SessionModel.reports))
    .all()
)
```

### 2. Efficient Database Queries
- **Severity**: Warning
- **Description**: Write efficient database queries
- **Best practices**:
  - Use indexes on frequently queried columns
  - Select only needed columns
  - Use pagination for large result sets
  - Avoid SELECT * in production
  - Use database-level filtering

**Example - Bad**:
```python
# Loads all sessions, filters in Python
all_sessions = session_repo.find_all()
active_sessions = [s for s in all_sessions if s.status == "active"]
```

**Example - Good**:
```python
# Filters in database
active_sessions = session_repo.find_by_status("active")
```

### 3. Appropriate Caching
- **Severity**: Warning
- **Description**: Cache expensive operations when appropriate
- **Cache candidates**:
  - Expensive computations
  - External API calls
  - Database queries for static data
  - Compiled templates

**Example**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_ansible_module_mapping() -> dict[str, str]:
    """Cache module mapping since it rarely changes."""
    return load_module_mapping_from_file()
```

**Redis caching**:
```python
async def get_session(session_id: UUID) -> Session:
    # Try cache first
    cached = await redis.get(f"session:{session_id}")
    if cached:
        return Session.parse_raw(cached)

    # Load from database
    session = await session_repo.find_by_id(session_id)

    # Cache for 1 hour
    await redis.setex(
        f"session:{session_id}",
        3600,
        session.json()
    )
    return session
```

### 4. No Unnecessary Loops
- **Severity**: Warning
- **Description**: Avoid inefficient loops and iterations
- **Optimize**:
  - Use list comprehensions instead of loops
  - Use built-in functions (map, filter, sum)
  - Avoid nested loops when possible
  - Use sets for membership testing

**Example - Bad**:
```python
# O(n²) complexity
result = []
for item in list1:
    for other in list2:
        if item == other:
            result.append(item)
```

**Example - Good**:
```python
# O(n) complexity using set intersection
result = list(set(list1) & set(list2))
```

### 5. Proper Async/Await Usage
- **Severity**: Warning
- **Description**: Use async properly for I/O-bound operations
- **Use async for**:
  - Database queries
  - HTTP requests
  - File I/O
  - External API calls

**Example - Bad**:
```python
async def process_sessions(session_ids: list[UUID]) -> list[Report]:
    reports = []
    for session_id in session_ids:
        session = await session_repo.find_by_id(session_id)  # Sequential!
        report = await compile_session(session)
        reports.append(report)
    return reports
```

**Example - Good**:
```python
async def process_sessions(session_ids: list[UUID]) -> list[Report]:
    # Parallel execution
    sessions = await asyncio.gather(*[
        session_repo.find_by_id(sid) for sid in session_ids
    ])
    reports = await asyncio.gather(*[
        compile_session(session) for session in sessions
    ])
    return reports
```

### 6. Memory Efficiency
- **Severity**: Warning
- **Description**: Avoid unnecessary memory usage
- **Best practices**:
  - Use generators for large datasets
  - Stream large files instead of loading into memory
  - Clean up resources (close files, connections)
  - Use context managers

**Example - Bad**:
```python
def process_large_file(path: str) -> list[str]:
    # Loads entire file into memory
    with open(path) as f:
        lines = f.readlines()
    return [process_line(line) for line in lines]
```

**Example - Good**:
```python
def process_large_file(path: str) -> Iterator[str]:
    # Streams file line by line
    with open(path) as f:
        for line in f:
            yield process_line(line)
```

## Performance Testing

### Benchmarking
```python
import time

def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@benchmark
def slow_operation():
    ...
```

### Profiling
```bash
# Profile with cProfile
python -m cProfile -o profile.stats script.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

## Performance Targets

- API endpoints: < 200ms p95
- Database queries: < 50ms p95
- Playbook compilation: < 1s for 100 commands
- Memory usage: < 512MB per worker

## Enforcement
- Performance regressions are flagged in reviews
- Benchmark critical paths
- Monitor production performance
- Optimize hot paths identified by profiling
