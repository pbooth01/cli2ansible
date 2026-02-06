"""HTTP API module with versioned routers."""

import logging

from cli2ansible.application import (
    CleanSessionService,
    CompilePlaybookService,
    IngestSessionService,
)
from cli2ansible.application.errors import ApplicationError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .v1 import create_v1_router

logger = logging.getLogger(__name__)


def create_app(
    ingest_service: IngestSessionService,
    compile_service: CompilePlaybookService,
    clean_service: CleanSessionService | None = None,
) -> FastAPI:
    """Create FastAPI application with API v1 routers."""
    app = FastAPI(title="cli2ansible", version="0.1.0")

    # Add CORS middleware to allow requests from the frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods including DELETE
        allow_headers=["*"],
    )

    # Global exception handlers
    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        _: Request, exc: ApplicationError
    ) -> JSONResponse:
        """Handle application layer errors with RFC7807 style responses."""
        payload = {
            "type": f"https://errors.cli2ansible.com/{exc.code}",
            "title": exc.code.replace("_", " ").title(),
            "detail": str(exc) or exc.code,
            "status": exc.status,
        }
        if exc.details:
            payload["errors"] = exc.details
        return JSONResponse(status_code=exc.status, content=payload)

    @app.exception_handler(Exception)
    async def catch_all_handler(_: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions with safe 500 response."""
        logger.exception("Unhandled exception in API")
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred",
            },
        )

    # Include v1 API router with all endpoints
    v1_router = create_v1_router(ingest_service, compile_service, clean_service)
    app.include_router(v1_router)

    return app


__all__ = ["create_app", "create_v1_router"]
