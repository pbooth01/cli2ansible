---
type: "always_apply"
---

# Architecture Rules

## Overview
This project follows **Hexagonal Architecture** (Ports and Adapters). These rules ensure architectural compliance.

## Architecture Principles

### Hexagonal Architecture
```
┌─────────────────────────────────────────┐
│           Inbound Adapters              │
│  (HTTP API, CLI, Message Queue)         │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼──────┐
        │   Ports     │ (Interfaces)
        └──────┬──────┘
               │
        ┌──────▼──────────────────────┐
        │      Domain Layer           │
        │  (Business Logic, Entities) │
        │  NO I/O DEPENDENCIES        │
        └──────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │   Ports     │ (Interfaces)
        └──────┬──────┘
               │
┌──────────────▼──────────────────────────┐
│         Outbound Adapters               │
│  (Database, S3, External APIs)          │
└─────────────────────────────────────────┘
```

## Rules

### 1. Hexagonal Architecture Compliance
- **Severity**: Warning
- **Description**: All code must follow hexagonal architecture pattern
- **Requirements**:
  - Domain layer is pure business logic
  - Adapters handle I/O and external systems
  - Ports define interfaces between layers
  - Dependencies point inward (adapters → domain)

### 2. Domain Has No I/O
- **Severity**: Warning
- **Description**: Domain layer must not perform I/O operations
- **Prohibited in domain**:
  - Database queries
  - HTTP requests
  - File system operations
  - External API calls
  - Logging (except domain events)

**Example - Bad**:
```python
# In domain/session.py
class Session:
    def save(self):
        db.execute("INSERT INTO sessions ...")  # ❌ I/O in domain
```

**Example - Good**:
```python
# In domain/entities/session.py
@dataclass
class Session:
    id: UUID
    name: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    # Pure data, no I/O

# In adapters/outbound/db/sqlalchemy_session_repo.py
class SQLAlchemySessionRepository(SessionRepositoryPort):
    def save(self, session: Session) -> Session:
        # I/O happens in adapter
        orm = SessionORM(...)
        self.db.add(orm)
        self.db.commit()
        return session
```

### 3. Proper Ports and Adapters
- **Severity**: Warning
- **Description**: Use ports (interfaces) to decouple layers
- **Requirements**:
  - Define port interfaces in domain layer
  - Implement adapters that satisfy ports
  - Inject adapters via dependency injection
  - Never import adapters in domain

**Example**:
```python
# domain/ports/repositories/session.py
class SessionRepositoryPort(ABC):
    @abstractmethod
    def save(self, session: Session) -> Session: ...

    @abstractmethod
    def get(self, session_id: UUID) -> Session | None: ...

    @abstractmethod
    def list_all(self) -> list[Session]: ...

    @abstractmethod
    def delete(self, session_id: UUID) -> None: ...

# adapters/outbound/db/sqlalchemy_session_repo.py
class SQLAlchemySessionRepository(SessionRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def save(self, session: Session) -> Session:
        # Implementation with SQLAlchemy
        orm = SessionORM.from_entity(session)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm.to_entity()
```

### 4. Dependency Injection
- **Severity**: Warning
- **Description**: Use dependency injection for loose coupling
- **Requirements**:
  - Inject dependencies via constructor
  - Don't create dependencies inside classes
  - Use interfaces, not concrete types
  - Configure DI in main/bootstrap

**Example**:
```python
# services/compile_playbook.py
class CompilePlaybook:
    def __init__(
        self,
        session_repo: SessionRepositoryPort,
        storage: StoragePort
    ):
        self.session_repo = session_repo
        self.storage = storage

    def compile(self, session: Session) -> Report:
        # Use injected dependencies
        ...
```

### 5. Separation of Concerns
- **Severity**: Warning
- **Description**: Each layer has a single responsibility
- **Layer responsibilities**:
  - **Domain**: Business logic, entities, domain events
  - **Services**: Application use cases, orchestration
  - **Adapters (Inbound)**: HTTP, CLI, message handling
  - **Adapters (Outbound)**: Database, S3, external APIs
  - **Ports**: Interface definitions


## Architectural Patterns

### Domain-Driven Design
- Use ubiquitous language (Session, Event, Command, Task, Role)
- Model domain concepts explicitly as entities
- Aggregate roots control consistency (Session is the aggregate root)
- Domain services encapsulate business logic (IngestSession, CompilePlaybook, CleanSession)
- Value objects for immutable concepts (TaskConfidence, SessionStatus)

### Application Layer Pattern
- Application services orchestrate use cases
- DTOs for data transfer across boundaries
- Use case ports define application interfaces
- Error handling at application boundary
- Translation between domain and API representations

### Repository Pattern
- Abstract data persistence behind ports
- Domain defines repository interfaces
- Adapters implement concrete repositories
- Separate repositories per aggregate (SessionRepository, EventRepository, CommandRepository)

### Dependency Injection
- All dependencies injected via constructors
- Composition root in `app.py`
- No service locator pattern
- Testable through interface injection

## Enforcement
- Architecture violations generate warnings
- Major violations may block merge
- Architectural reviews required for structural changes
- Refactoring should maintain architecture
