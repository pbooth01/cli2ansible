"""Health check router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "cli2ansible"}
