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
# In domain/session.py
@dataclass
class Session:
    id: UUID
    name: str
    commands: list[str]
    # Pure data, no I/O

# In adapters/outbound/persistence/session_repository.py
class SessionRepository:
    def save(self, session: Session) -> None:
        # I/O happens in adapter
        self.db.execute(...)
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
# domain/ports/session_repository.py
class SessionRepositoryPort(ABC):
    @abstractmethod
    def save(self, session: Session) -> None: ...

    @abstractmethod
    def find_by_id(self, session_id: UUID) -> Optional[Session]: ...

# adapters/outbound/persistence/session_repository.py
class SessionRepository(SessionRepositoryPort):
    def __init__(self, db: Database):
        self.db = db

    def save(self, session: Session) -> None:
        # Implementation
        ...
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

### 6. Layer Structure
- **Severity**: Warning
- **Description**: Follow the established directory structure
- **Required structure**:
```
src/cli2ansible/
├── domain/              # Entities, value objects, domain logic
│   ├── session.py
│   ├── report.py
│   └── ports/          # Port interfaces
│       ├── session_repository.py
│       └── storage.py
├── services/           # Application services (use cases)
│   └── compile_playbook.py
└── adapters/
    ├── inbound/        # Entry points
    │   ├── http/       # HTTP API
    │   └── cli/        # CLI interface
    └── outbound/       # External integrations
        ├── persistence/  # Database
        └── storage/      # S3/MinIO
```

## Architectural Patterns

### Domain-Driven Design
- Use ubiquitous language
- Model domain concepts explicitly
- Aggregate roots control consistency
- Domain events for side effects

### CQRS (if applicable)
- Separate read and write models
- Commands modify state
- Queries return data
- No business logic in queries

## Enforcement
- Architecture violations generate warnings
- Major violations may block merge
- Architectural reviews required for structural changes
- Refactoring should maintain architecture
