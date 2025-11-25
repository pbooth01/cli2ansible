"""API v1 routers."""

from typing import Any

from fastapi import APIRouter

from . import health
from .cast import create_router as create_cast_router
from .events import create_router as create_events_router
from .sessions import create_router as create_sessions_router


def create_v1_router(
    ingest_service: Any, compile_service: Any, clean_service: Any = None
) -> APIRouter:
    """Create and return the v1 API router with all sub-routers."""
    router = APIRouter(prefix="/api/v1")

    # Include health check (no dependencies)
    router.include_router(health.router)

    # Include consolidated sessions router (CRUD + compile + report + clean)
    router.include_router(
        create_sessions_router(ingest_service, compile_service, clean_service)
    )

    # Include cast file router
    router.include_router(create_cast_router(ingest_service, compile_service))

    # Include events router
    router.include_router(create_events_router(ingest_service))

    return router
