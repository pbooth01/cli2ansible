# Backend API Conventions

## Framework

- **FastAPI** for REST APIs
- **Pydantic v2** for request/response schemas
- **SQLAlchemy 2.0** for database

## API Design

### Versioning

- All endpoints prefixed with `/v1/` (future versions: `/v2/`)
- No breaking changes within a version
- Deprecation warnings for 2+ releases before removal

### Request/Response

```python
# Request schema
class SessionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)

# Response schema
class SessionResponse(BaseModel):
    id: UUID
    name: str
    status: str
    created_at: datetime
```

### HTTP Methods

- **GET**: Read-only, idempotent, cacheable
- **POST**: Create resources, non-idempotent
- **PUT**: Full update, idempotent
- **PATCH**: Partial update
- **DELETE**: Remove resource, idempotent

### Status Codes

- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource state conflict
- **422 Unprocessable Entity**: Validation failed
- **500 Internal Server Error**: Unexpected error

## Error Responses

```python
# Standard error format
{
    "error": {
        "code": "SESSION_NOT_FOUND",
        "message": "Session abc-123 not found",
        "details": {
            "session_id": "abc-123"
        }
    }
}
```

## Authentication & Authorization

- Use Bearer tokens in `Authorization` header
- Validate tokens on every request
- Return 401 for invalid/expired tokens
- Return 403 for insufficient permissions
- Never expose internal error details to clients

## Input Validation

```python
@app.post("/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate) -> Any:
    """Create a new session.

    Pydantic validates:
    - name is 1-255 chars
    - metadata is valid JSON
    """
    domain_session = ingest_service.create_session(
        name=session.name,
        metadata=session.metadata
    )
    return SessionResponse(...)
```

## Database Sessions

```python
# Use repository pattern - no direct SQLAlchemy in routes
@app.get("/sessions/{session_id}")
async def get_session(session_id: UUID) -> SessionResponse:
    session = repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(...)
```

## Logging

```python
import structlog

logger = structlog.get_logger()

@app.post("/sessions")
async def create_session(session: SessionCreate):
    logger.info(
        "session.create.start",
        name=session.name,
    )
    # ... create session ...
    logger.info(
        "session.create.success",
        session_id=str(result.id),
        name=result.name,
    )
```

## API Documentation

- FastAPI auto-generates OpenAPI docs at `/docs`
- Add descriptions to endpoints and schemas
- Include examples for complex schemas

```python
class SessionCreate(BaseModel):
    """Request to create a new session."""

    name: str = Field(
        ...,
        description="Human-readable session name",
        example="nginx-deployment"
    )
```

## Rate Limiting

- Implement rate limiting for public endpoints
- Return `429 Too Many Requests` with `Retry-After` header
- Document rate limits in API docs

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Health Checks

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies dependencies."""
    try:
        # Check database
        repo.health_check()
        # Check object storage
        store.health_check()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Not ready")
```

## Pagination

```python
class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_more: bool

@app.get("/sessions")
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    ...
```

## File Uploads

```python
@app.post("/sessions/{session_id}/recording")
async def upload_recording(
    session_id: UUID,
    file: UploadFile,
):
    # Validate file size
    if file.size > 10_000_000:  # 10MB
        raise HTTPException(400, "File too large")

    # Validate content type
    if file.content_type != "application/json":
        raise HTTPException(400, "Invalid content type")

    data = await file.read()
    # Process...
```

## Testing

```python
from fastapi.testclient import TestClient

def test_create_session(client: TestClient):
    response = client.post(
        "/sessions",
        json={"name": "test-session", "metadata": {}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-session"
    assert "id" in data
```
