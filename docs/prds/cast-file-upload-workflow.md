# Feature: Cast File Upload Workflow with Event Editing

**Status:** Draft
**Owner:** Engineering Team
**Created:** 2025-11-06
**Last Updated:** 2025-11-06 (v2 - added batch event updates)

## 1. Summary

**Problem:** Currently, users must manually parse .cast files locally and then upload events via API in a two-step process. There's no way to review and edit parsed events before compilation, which makes it difficult to correct parsing errors or adjust event data. Events also lack identifiers and versioning, making them immutable once uploaded.

**Solution:** Enable direct .cast file upload after session creation. The file is stored in MinIO, automatically parsed into events, and linked to the session. Events gain unique identifiers and version numbers, enabling PATCH operations. Users can review parsed events, edit them if needed, then compile the session using the familiar workflow.

**Success Metric:** Users can upload a .cast file, receive parsed events, edit events if needed (with 100% of edits persisting correctly), and compile sessions with the same success rate (>80% high confidence) as the current workflow.

## 2. Goals & Non-Goals

### Goals
- Support direct .cast file upload to existing sessions via API
- Store .cast files in MinIO with proper session linkage
- Automatically parse uploaded .cast files into events
- Return parsed events to user for review/editing
- Add unique identifiers to Event model for granular updates
- Add version tracking to Event model for optimistic locking
- Support PATCH operations on individual events
- Support batch event updates in a single API call
- Maintain backward compatibility with existing event upload workflow
- Follow hexagonal architecture patterns

### Non-Goals
- Real-time .cast file streaming (file-based only)
- Web UI for event editing (API-only for v1)
- .cast file format conversion or modification
- Direct .cast file download by users (original file retrieval)
- Support for non-.cast file formats
- Automatic event correction/suggestion (user-driven edits only)

## 3. Users & Use Cases

### Target Users
- **Persona 1**: DevOps Engineers recording terminal sessions
  - Experience level: Intermediate
  - Pain point: Multi-step process to get from recording to compilation; can't fix parsing errors
  - Benefit: Single file upload with ability to review and correct events

- **Persona 2**: Automation Engineers debugging workflows
  - Experience level: Advanced
  - Pain point: Parser sometimes misinterprets commands; no way to fix without re-recording
  - Benefit: Edit parsed events to correct mistakes before compilation

### Use Cases

#### Use Case 1: Simple Cast File Upload and Compile
**Actor:** DevOps Engineer
**Trigger:** Has a .cast file ready to convert to Ansible
**Flow:**
1. Create session: `POST /sessions` → get session_id
2. Upload .cast file: `POST /sessions/{id}/cast` with file
3. Receive parsed events in response with event IDs and versions
4. Review events (look good!)
5. Compile: `POST /sessions/{id}/compile`
6. Download playbook

**Success Criteria:**
- .cast file uploaded in one request
- Events parsed and stored automatically
- No manual event upload needed
- Compilation works as before

#### Use Case 2: Cast File Upload with Batch Event Editing
**Actor:** Automation Engineer
**Trigger:** Parser incorrectly extracted multiple command timestamps
**Flow:**
1. Create session: `POST /sessions` → get session_id
2. Upload .cast file: `POST /sessions/{id}/cast` with file
3. Receive parsed events with IDs and versions
4. Notice events #5, #12, and #20 have wrong timestamps
5. Update events: `PATCH /sessions/{id}/events` with array of event updates
6. Receive updated events with incremented versions
7. Compile: `POST /sessions/{id}/compile`
8. Events compiled correctly with fixed timestamps

**Success Criteria:**
- Can identify specific events by ID
- Can update multiple events in a single API call
- Version tracking prevents lost updates for all events
- Updated events persist through compilation
- Failed updates for some events don't block others (partial success)

#### Use Case 3: Handling Parse Errors Gracefully
**Actor:** DevOps Engineer
**Trigger:** Upload .cast file that fails parsing
**Flow:**
1. Create session: `POST /sessions` → get session_id
2. Upload .cast file: `POST /sessions/{id}/cast` with invalid file
3. Receive 400 error with clear message: "Invalid .cast format: line 5: expected array"
4. Fix .cast file locally
5. Upload again: `POST /sessions/{id}/cast` (replaces previous attempt)
6. Receive parsed events successfully
7. Compile session

**Success Criteria:**
- Clear error messages for parse failures
- Can retry upload after fixing file
- Previous failed upload doesn't block retry

## 4. Requirements

### Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | POST /sessions/{id}/cast accepts multipart/form-data with .cast file | P0 | Core upload functionality |
| FR-2 | Upload stores .cast file in MinIO at sessions/{id}/recording.cast | P0 | Durable storage |
| FR-3 | Upload triggers automatic parsing using AsciinemaParser | P0 | Reuse existing parser |
| FR-4 | Upload returns parsed events with id and version fields | P0 | Enable editing workflow |
| FR-5 | Event model gains id (UUID) and version (int) fields | P0 | Required for PATCH |
| FR-6 | GET /sessions/{id}/events returns all events for session | P0 | Review parsed events |
| FR-7 | PATCH /sessions/{id}/events updates multiple events in batch | P0 | Core editing |
| FR-8 | PATCH /sessions/{id}/events/{event_id} updates single event | P1 | Single-event editing |
| FR-9 | PATCH enforces optimistic locking via version field | P0 | Prevent lost updates |
| FR-10 | Batch PATCH supports partial success (some fail, some succeed) | P0 | Robustness |
| FR-11 | Session.metadata tracks cast_file_key when uploaded | P1 | Audit trail |
| FR-12 | Upload validates file is .cast format before storage | P0 | Fail fast |
| FR-13 | Upload enforces size limit (10MB default, same as parser) | P0 | DoS prevention |
| FR-14 | Existing POST /sessions/{id}/events workflow still works | P0 | Backward compat |
| FR-15 | Compile uses events from database regardless of source | P0 | Unified workflow |

### Non-Functional Requirements

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-1 | .cast file upload response time | < 10 seconds for 10MB file | P0 |
| NFR-2 | Parse large .cast files (100K events) | < 5 seconds | P0 |
| NFR-3 | Event PATCH response time | < 500ms | P0 |
| NFR-4 | MinIO upload reliability | 99.9% success rate | P0 |
| NFR-5 | Test coverage for new code | > 95% | P0 |
| NFR-6 | Concurrent uploads per session | 1 (reject if in progress) | P1 |
| NFR-7 | Database indexing on event.id | Unique index | P0 |
| NFR-8 | Database indexing on event.version | No index needed | P2 |

### Security Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| SEC-1 | Validate file is legitimate .cast format (not arbitrary file upload) | P0 |
| SEC-2 | Enforce file size limit to prevent DoS (10MB max) | P0 |
| SEC-3 | Validate session exists before accepting .cast upload | P0 |
| SEC-4 | Validate event_id exists before PATCH | P0 |
| SEC-5 | Validate version matches current version on PATCH (optimistic lock) | P0 |
| SEC-6 | Sanitize MinIO keys to prevent path traversal | P0 |
| SEC-7 | No command execution during parsing (already satisfied) | P0 |
| SEC-8 | Rate limit cast file uploads (per IP/user) | P1 |

### Compliance Requirements
- Same as existing system: recordings may contain PII/secrets
- Document that .cast files are stored indefinitely in MinIO
- Privacy: .cast files stored with session_id linkage for audit

## 5. UX/Interfaces

### API Endpoints

#### POST /sessions/{session_id}/cast
Upload a .cast file to a session.

**Request:**
```http
POST /sessions/550e8400-e29b-41d4-a716-446655440000/cast
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="recording.cast"
Content-Type: application/json

<.cast file contents>
--boundary--
```

**Response (200):**
```json
{
  "status": "parsed",
  "cast_file_key": "sessions/550e8400-e29b-41d4-a716-446655440000/recording.cast",
  "event_count": 42,
  "events": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": 1.234,
      "event_type": "o",
      "data": "echo hello",
      "sequence": 0,
      "version": 1
    },
    ...
  ]
}
```

**Response (400) - Invalid Format:**
```json
{
  "detail": "Invalid .cast file format: line 1: expected JSON object header"
}
```

**Response (404) - Session Not Found:**
```json
{
  "detail": "Session not found"
}
```

**Response (413) - File Too Large:**
```json
{
  "detail": "File size (15728640 bytes) exceeds maximum (10485760 bytes)"
}
```

#### GET /sessions/{session_id}/events
Get all events for a session (new endpoint).

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_count": 42,
  "events": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": 1.234,
      "event_type": "o",
      "data": "echo hello",
      "sequence": 0,
      "version": 1
    },
    ...
  ]
}
```

#### PATCH /sessions/{session_id}/events
Update multiple events in a batch (primary editing endpoint).

**Request:**
```json
{
  "updates": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "version": 1,
      "timestamp": 1.5,
      "data": "echo hello world"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440012",
      "version": 1,
      "timestamp": 5.2
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440020",
      "version": 1,
      "data": "cd /opt/app"
    }
  ]
}
```

**Response (200):**
```json
{
  "updated": 3,
  "failed": 0,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "success",
      "event": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": 1.5,
        "event_type": "o",
        "data": "echo hello world",
        "sequence": 0,
        "version": 2
      }
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440012",
      "status": "success",
      "event": {
        "id": "660e8400-e29b-41d4-a716-446655440012",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": 5.2,
        "event_type": "o",
        "data": "ls -la",
        "sequence": 5,
        "version": 2
      }
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440020",
      "status": "success",
      "event": {
        "id": "660e8400-e29b-41d4-a716-446655440020",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": 8.1,
        "event_type": "o",
        "data": "cd /opt/app",
        "sequence": 10,
        "version": 2
      }
    }
  ]
}
```

**Response (207 Multi-Status) - Partial Success:**
```json
{
  "updated": 2,
  "failed": 1,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "success",
      "event": { ... }
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440012",
      "status": "error",
      "error": "Version conflict: expected version 1, current is 2"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440020",
      "status": "success",
      "event": { ... }
    }
  ]
}
```

**Response (400) - Invalid Request:**
```json
{
  "detail": "updates field is required and must contain at least one update"
}
```

#### PATCH /sessions/{session_id}/events/{event_id}
Update a single event (convenience endpoint for single edits).

**Request:**
```json
{
  "version": 1,
  "timestamp": 1.5,
  "data": "echo hello world"
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1.5,
  "event_type": "o",
  "data": "echo hello world",
  "sequence": 0,
  "version": 2
}
```

**Response (409) - Version Conflict:**
```json
{
  "detail": "Version conflict: expected version 2, got 1. Event was modified by another process."
}
```

**Response (404) - Event Not Found:**
```json
{
  "detail": "Event not found"
}
```

#### Existing Endpoints (No Changes)
- `POST /sessions` - create session (unchanged)
- `POST /sessions/{id}/events` - upload events manually (still works)
- `POST /sessions/{id}/compile` - compile session (unchanged)
- `GET /sessions/{id}/report` - get report (unchanged)

## 6. Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     HTTP Layer                          │
│  POST /sessions/{id}/cast                               │
│  - Accept multipart file upload                         │
│  - Validate session exists                              │
│  - Coordinate storage + parsing                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│               Domain Service Layer                      │
│  IngestSession.upload_cast_file()                       │
│  - Store file in MinIO                                  │
│  - Parse file to events                                 │
│  - Save events with IDs/versions                        │
│  - Update session metadata                              │
└───────┬─────────────────────────┬───────────────────────┘
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────────┐
│  ObjectStore │          │  AsciinemaParser │
│  (MinIO)     │          │  (existing)      │
│              │          │                  │
│  - upload()  │          │  - parse_events()│
└──────────────┘          └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│              Session Repository                         │
│  - save_events() (enhanced with id/version)             │
│  - get_events()                                         │
│  - update_event() (new)                                 │
│  - get_event_by_id() (new)                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   PostgreSQL                            │
│  events table (add id UUID, version INT)                │
└─────────────────────────────────────────────────────────┘
```

### Data Model Changes

**Before (Event):**
```python
@dataclass
class Event:
    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int = 0
```

**After (Event):**
```python
@dataclass
class Event:
    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int = 0
    id: UUID = field(default_factory=uuid4)  # NEW
    version: int = 1  # NEW
```

**ORM Changes (EventORM):**
```python
class EventORM(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))  # CHANGED
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    event_type: Mapped[str] = mapped_column(String(10), nullable=False)
    data: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # NEW
```

**Migration Required:**
```sql
-- Migration: Add id and version to events table
ALTER TABLE events ADD COLUMN id_new VARCHAR(36);
ALTER TABLE events ADD COLUMN version INTEGER DEFAULT 1 NOT NULL;

-- Populate existing events with UUIDs
UPDATE events SET id_new = gen_random_uuid()::text;

-- Drop old auto-increment id, rename id_new to id
ALTER TABLE events DROP CONSTRAINT events_pkey;
ALTER TABLE events DROP COLUMN id;
ALTER TABLE events RENAME COLUMN id_new TO id;
ALTER TABLE events ADD PRIMARY KEY (id);

-- Add index
CREATE UNIQUE INDEX idx_events_id ON events(id);
```

### Component Design

#### IngestSession Service (Enhanced)

```python
class IngestSession:
    def __init__(
        self,
        repo: SessionRepositoryPort,
        parser: CapturePort,
        store: ObjectStorePort
    ) -> None:
        self.repo = repo
        self.parser = parser
        self.store = store

    def upload_cast_file(
        self,
        session_id: UUID,
        file_data: bytes,
        filename: str
    ) -> list[Event]:
        """
        Upload .cast file, store in MinIO, parse, and save events.

        Returns parsed events with IDs and versions.

        Raises:
            ValueError: If session not found or file invalid
        """
        # 1. Validate session exists
        session = self.repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 2. Validate file size
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            raise ValueError(f"File size exceeds maximum (10MB)")

        # 3. Parse file to validate format
        try:
            events = self.parser.parse_events(file_data)
        except ValueError as e:
            raise ValueError(f"Invalid .cast file format: {e}")

        # 4. Store file in MinIO
        key = f"sessions/{session_id}/recording.cast"
        self.store.upload(key, file_data, "application/json")

        # 5. Assign event IDs and versions
        for event in events:
            event.id = uuid4()
            event.session_id = session_id
            event.version = 1

        # 6. Save events to database
        self.repo.save_events(events)

        # 7. Update session metadata and status
        session.metadata["cast_file_key"] = key
        session.metadata["cast_filename"] = filename
        session.status = SessionStatus.UPLOADED
        self.repo.update(session)

        return events

    def update_events_batch(
        self,
        session_id: UUID,
        updates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Update multiple events in a batch with partial success support.

        Returns list of results with status for each update.
        Each result: {"id": UUID, "status": "success"|"error", "event": Event | None, "error": str | None}

        Note: Uses individual transactions per event to enable partial success.
        """
        results = []

        for update_spec in updates:
            event_id = update_spec["id"]
            expected_version = update_spec["version"]

            try:
                event = self.repo.get_event_by_id(event_id)
                if not event:
                    results.append({
                        "id": event_id,
                        "status": "error",
                        "error": f"Event {event_id} not found"
                    })
                    continue

                if event.session_id != session_id:
                    results.append({
                        "id": event_id,
                        "status": "error",
                        "error": "Event does not belong to this session"
                    })
                    continue

                if event.version != expected_version:
                    results.append({
                        "id": event_id,
                        "status": "error",
                        "error": f"Version conflict: expected {expected_version}, current is {event.version}"
                    })
                    continue

                # Apply updates
                for key, value in update_spec.items():
                    if key in ("timestamp", "data", "event_type"):
                        setattr(event, key, value)

                # Increment version
                event.version += 1

                # Save
                self.repo.update_event(event)

                results.append({
                    "id": event_id,
                    "status": "success",
                    "event": event
                })

            except Exception as e:
                results.append({
                    "id": event_id,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def update_event(
        self,
        session_id: UUID,
        event_id: UUID,
        updates: dict[str, Any],
        expected_version: int
    ) -> Event:
        """
        Update a single event with optimistic locking (convenience method).

        Raises:
            ValueError: If event not found
            VersionConflictError: If version mismatch
        """
        event = self.repo.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        if event.session_id != session_id:
            raise ValueError("Event does not belong to this session")

        if event.version != expected_version:
            raise VersionConflictError(
                f"Version conflict: expected {expected_version}, "
                f"current is {event.version}"
            )

        # Apply updates
        for key, value in updates.items():
            if key in ("timestamp", "data", "event_type"):
                setattr(event, key, value)

        # Increment version
        event.version += 1

        # Save
        self.repo.update_event(event)
        return event
```

#### SessionRepositoryPort (Enhanced)

```python
class SessionRepositoryPort(ABC):
    # Existing methods...

    @abstractmethod
    def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Retrieve a single event by ID."""
        ...

    @abstractmethod
    def update_event(self, event: Event) -> Event:
        """Update an event (increments version)."""
        ...
```

#### API Schemas (New)

```python
class CastUploadResponse(BaseModel):
    """Response schema for cast file upload."""
    status: str
    cast_file_key: str
    event_count: int
    events: list[EventResponse]


class EventResponse(BaseModel):
    """Response schema for event with ID and version."""
    id: UUID
    session_id: UUID
    timestamp: float
    event_type: str
    data: str
    sequence: int
    version: int


class EventUpdateRequest(BaseModel):
    """Request schema for updating a single event."""
    version: int = Field(..., description="Current version for optimistic locking")
    timestamp: float | None = None
    data: str | None = None
    event_type: str | None = None

    @validator('event_type')
    def validate_event_type(cls, v):
        if v and v not in ('i', 'o', 'x'):
            raise ValueError("event_type must be 'i', 'o', or 'x'")
        return v


class BatchEventUpdate(BaseModel):
    """Single event update in a batch request."""
    id: UUID = Field(..., description="Event ID to update")
    version: int = Field(..., description="Current version for optimistic locking")
    timestamp: float | None = None
    data: str | None = None
    event_type: str | None = None

    @validator('event_type')
    def validate_event_type(cls, v):
        if v and v not in ('i', 'o', 'x'):
            raise ValueError("event_type must be 'i', 'o', or 'x'")
        return v


class BatchEventUpdateRequest(BaseModel):
    """Request schema for batch event updates."""
    updates: list[BatchEventUpdate] = Field(..., min_items=1, description="List of event updates")


class EventUpdateResult(BaseModel):
    """Result of a single event update in batch."""
    id: UUID
    status: Literal["success", "error"]
    event: EventResponse | None = None
    error: str | None = None


class BatchEventUpdateResponse(BaseModel):
    """Response schema for batch event updates."""
    updated: int = Field(..., description="Number of successfully updated events")
    failed: int = Field(..., description="Number of failed updates")
    results: list[EventUpdateResult]


class EventsListResponse(BaseModel):
    """Response schema for list of events."""
    session_id: UUID
    event_count: int
    events: list[EventResponse]
```

### Error Handling

| Error Condition | HTTP Status | Response | Recovery |
|----------------|-------------|----------|----------|
| Session not found | 404 | "Session not found" | Create session first |
| .cast file too large | 413 | "File size exceeds 10MB" | Split or reduce file |
| Invalid .cast format | 400 | "Invalid .cast format: {detail}" | Fix file, retry |
| Event not found (single) | 404 | "Event not found" | Check event ID |
| Version conflict (single) | 409 | "Version conflict: expected X, got Y" | Refetch and retry |
| Batch update partial failure | 207 | Multi-status with per-event results | Review failures, retry failed ones |
| Batch update empty | 400 | "updates field must contain at least one update" | Provide updates |
| Parse error (empty) | 400 | "Empty .cast file" | Use valid file |
| Parse error (encoding) | 400 | "Invalid UTF-8 encoding" | Fix encoding |
| MinIO upload failure | 500 | "Storage error" | Retry |

### Data Flow: Cast File Upload

```
User uploads .cast → POST /sessions/{id}/cast
    ↓
    validate session exists → 404 if not found
    ↓
    validate file size → 413 if too large
    ↓
    parse_events(file_data) → 400 if invalid format
    ↓
    store file in MinIO → sessions/{id}/recording.cast
    ↓
    assign IDs and versions to events
    ↓
    save events to database
    ↓
    update session.status = UPLOADED
    ↓
    update session.metadata["cast_file_key"]
    ↓
    return events with IDs/versions
```

### Data Flow: Batch Event Update

```
User edits events → PATCH /sessions/{id}/events with updates array
    ↓
    validate request has at least one update → 400 if empty
    ↓
    for each update:
        ↓
        validate event exists → record error if not found
        ↓
        validate event.session_id matches → record error if mismatch
        ↓
        validate version matches → record error if mismatch
        ↓
        apply updates (timestamp, data, event_type)
        ↓
        increment version
        ↓
        save to database → record success or error
    ↓
    return 200 (all success) or 207 (partial success) with results
```

### Data Flow: Single Event Update

```
User edits event → PATCH /sessions/{id}/events/{event_id}
    ↓
    validate event exists → 404 if not found
    ↓
    validate event.session_id matches → 400 if mismatch
    ↓
    validate version matches → 409 if mismatch
    ↓
    apply updates (timestamp, data, event_type)
    ↓
    increment version
    ↓
    save to database
    ↓
    return updated event
```

## 7. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Database migration fails for existing events | High | Low | Thorough migration testing; rollback plan; backward compat |
| Large .cast files cause memory issues | Medium | Medium | Enforce 10MB limit; streaming parse if needed (future) |
| Version conflicts frustrate users | Medium | Low | Clear error messages; document retry pattern |
| MinIO storage costs increase | Low | High | Expected; document storage policy; add cleanup job (future) |
| Existing code breaks with Event model changes | High | Medium | Comprehensive test coverage; default values for new fields |
| Parser performance degrades with ID assignment | Low | Low | ID generation is fast (UUID4); negligible overhead |
| Concurrent uploads corrupt data | Medium | Low | Enforce single upload per session; transaction safety |

## 8. Rollout & Metrics

### Rollout Plan

**Phase 1: Database Migration (Week 1)**
- ✅ Add id and version columns to events table
- ✅ Generate UUIDs for existing events
- ✅ Test migration on staging with production data snapshot
- ✅ Verify backward compatibility with existing events

**Phase 2: Domain Model Updates (Week 1)**
- Update Event dataclass with id and version fields
- Update EventORM with new columns
- Add default values to ensure existing code works
- Update repository methods to handle new fields
- Unit tests for model changes

**Phase 3: Repository Enhancements (Week 2)**
- Implement get_event_by_id() method
- Implement update_event() method
- Add optimistic locking logic
- Unit tests for repository methods

**Phase 4: Service Layer (Week 2)**
- Implement upload_cast_file() in IngestSession
- Implement update_event() in IngestSession
- Add VersionConflictError exception
- Service integration tests

**Phase 5: API Endpoints (Week 3)**
- POST /sessions/{id}/cast endpoint
- GET /sessions/{id}/events endpoint
- PATCH /sessions/{id}/events/{event_id} endpoint
- Pydantic schemas for request/response
- API integration tests

**Phase 6: Testing & QA (Week 3)**
- End-to-end tests for full workflow
- Load testing with 10MB files
- Concurrent request testing
- Error scenario testing
- Security testing

**Phase 7: Documentation (Week 4)**
- API documentation updates
- Migration guide for existing users
- Example workflows
- Troubleshooting guide

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Upload success rate | > 99% | API logs |
| Parse success rate | > 95% for valid .cast | Parser metrics |
| PATCH success rate (all events in batch) | > 99% | API logs |
| Batch PATCH partial success rate | < 5% | 207 responses / total batch requests |
| Version conflict rate | < 1% | Conflict errors / total event updates |
| Upload latency p95 | < 10s for 10MB | API metrics |
| Single PATCH latency p95 | < 500ms | API metrics |
| Batch PATCH latency p95 | < 2s for 100 events | API metrics |
| Test coverage | > 95% | pytest-cov |
| Zero data loss | 100% | Audit logs |

### Monitoring

**Key Metrics:**
- Cast file upload count (per hour)
- Parse failures (count + reasons)
- Event PATCH count
- Version conflicts (count)
- MinIO storage usage (GB)
- API latency by endpoint (p50, p95, p99)
- Error rate by endpoint

**Alerts:**
- Upload failure rate > 5%
- Parse failure rate > 10%
- MinIO storage > 80% capacity
- API latency p95 > 15s
- Version conflict rate > 5%

### Rollback Strategy

If critical issues discovered:
1. **Immediate:** Disable POST /sessions/{id}/cast endpoint (return 503)
2. **Short-term:** Users can still use POST /sessions/{id}/events (old workflow)
3. **Fix:** Resolve issue in staging
4. **Gradual re-enable:** 10% traffic → 50% → 100%

Database rollback:
- Revert migration only if absolutely necessary
- id and version columns can coexist without breaking old code
- New code checks for field existence before using

## 9. Open Questions

| Question | Owner | Target Date | Status |
|----------|-------|-------------|--------|
| Should we support re-uploading .cast to same session (replace)? | PM | 2025-11-08 | Open |
| Should batch PATCH abort on first failure or continue? | Engineering | 2025-11-08 | Closed: Continue (partial success) |
| What's the retention policy for .cast files in MinIO? | PM | 2025-11-12 | Open |
| Should we expose .cast file download endpoint? | PM | 2025-11-12 | Open |
| Should we validate event sequence numbers after edits? | Engineering | 2025-11-10 | Open |
| Should batch PATCH be transactional (all-or-nothing)? | Engineering | 2025-11-08 | Closed: No (per-event transactions) |
| Should we support DELETE /events/{id}? | PM | 2025-11-15 | Closed: No (defer to v2) |
| What's the max batch size for event updates? | Engineering | 2025-11-10 | Open: Suggest 1000 |

## 10. Dependencies

### Internal Dependencies
- Existing AsciinemaParser (reuse for parsing)
- ObjectStorePort and S3ObjectStore (MinIO integration)
- SessionRepositoryPort (enhance with new methods)
- IngestSession service (enhance with upload logic)
- FastAPI app (add new endpoints)

### External Dependencies
- PostgreSQL (database migration required)
- MinIO (S3-compatible storage)
- Python multipart file handling (python-multipart library)

### Blocking Issues
- Database migration must complete before deployment
- Backward compatibility testing with existing sessions required

## 11. Alternatives Considered

### Alternative 1: Store Events Only (No Cast File Storage)
**Pros:** Simpler; less storage cost; fewer moving parts
**Cons:** Can't re-parse if parser improves; no audit trail of original file; can't debug parsing issues
**Decision:** Rejected - audit trail valuable for debugging

### Alternative 2: Parse on Demand (Don't Store Events Until Compile)
**Pros:** Saves database storage; parse only when needed
**Cons:** Can't edit events; slower compile; no intermediate review; parse errors delay compilation
**Decision:** Rejected - defeats purpose of editing workflow

### Alternative 3: Use PUT Instead of PATCH for Events
**Pros:** Simpler semantics (replace entire event)
**Cons:** More data sent; riskier (accidental field omission); less RESTful for partial updates
**Decision:** Rejected - PATCH is correct for partial updates

### Alternative 4: Event Versioning via Timestamp
**Pros:** No version field needed; simpler model
**Cons:** Clock skew issues; concurrent updates still conflict; less explicit
**Decision:** Rejected - integer version is standard for optimistic locking

### Alternative 5: No Event Editing (Accept Parser Output As-Is)
**Pros:** Much simpler implementation; no versioning needed; faster development
**Cons:** No way to fix parsing errors; blocks users when parser fails; bad UX
**Decision:** Rejected - editing is core requirement from user request

### Alternative 6: Transactional Batch Updates (All-or-Nothing)
**Pros:** Simpler error handling; atomic operations; easier to reason about
**Cons:** One failing event blocks all updates; poor UX; requires rollback mechanism
**Decision:** Rejected - partial success is more user-friendly and robust

## 12. References

- [Asciinema Format Documentation](https://github.com/asciinema/asciinema/blob/develop/doc/asciicast-v2.md)
- [Optimistic Locking Pattern](https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html)
- [HTTP PATCH Method](https://datatracker.ietf.org/doc/html/rfc5789)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [SQLAlchemy Migration Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- Existing PRD: docs/prds/asciinema-cast-converter.md (parser implementation)

## 13. Appendix

### Glossary

- **Cast File**: Asciinema .cast recording file (JSON lines format)
- **Event**: Single terminal event (input/output) from recording
- **Event ID**: Unique identifier (UUID) for an event, enables PATCH operations
- **Version**: Integer tracking edit count; enables optimistic locking
- **Optimistic Locking**: Concurrency control where version is checked before update
- **Session**: Container for a terminal recording workflow
- **MinIO**: S3-compatible object storage for artifacts

### Example Workflows

#### Workflow 1: Happy Path (No Edits)
```bash
# 1. Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "nginx-setup"}'
# Response: {"id": "550e8400-...", "status": "created"}

# 2. Upload .cast file
curl -X POST http://localhost:8000/sessions/550e8400-.../cast \
  -F "file=@recording.cast"
# Response: {"status": "parsed", "event_count": 42, "events": [...]}

# 3. Compile (no edits needed)
curl -X POST http://localhost:8000/sessions/550e8400-.../compile
# Response: {"artifact_url": "...", "download_url": "..."}
```

#### Workflow 2: With Batch Event Editing
```bash
# 1-2. Same as above (create session, upload cast)

# 3. Get events to review
curl http://localhost:8000/sessions/550e8400-.../events
# Response: {"event_count": 42, "events": [...]}

# 4. Notice events 5, 12, and 20 have wrong timestamps, update them in batch
curl -X PATCH http://localhost:8000/sessions/550e8400-.../events \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {"id": "660e8400-...001", "version": 1, "timestamp": 2.5},
      {"id": "660e8400-...012", "version": 1, "timestamp": 5.2},
      {"id": "660e8400-...020", "version": 1, "data": "cd /opt/app"}
    ]
  }'
# Response: {"updated": 3, "failed": 0, "results": [...]}

# 5. Compile with corrected events
curl -X POST http://localhost:8000/sessions/550e8400-.../compile
# Response: {"artifact_url": "...", "download_url": "..."}
```

#### Workflow 3: Single Event Edit (Convenience)
```bash
# 1-2. Same as above (create session, upload cast)

# 3. Update a single event using the convenience endpoint
curl -X PATCH http://localhost:8000/sessions/550e8400-.../events/660e8400-... \
  -H "Content-Type: application/json" \
  -d '{"version": 1, "timestamp": 2.5}'
# Response: {"id": "660e8400-...", "timestamp": 2.5, "version": 2}

# 4. Compile
curl -X POST http://localhost:8000/sessions/550e8400-.../compile
# Response: {"artifact_url": "...", "download_url": "..."}
```

### Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-06 | Initial draft based on user feature request | PRDAgent |
| 2025-11-06 | Added batch event update support (PATCH /sessions/{id}/events) | Engineering |
