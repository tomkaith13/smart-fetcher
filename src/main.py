"""FastAPI application entry point for smart-fetcher."""

from contextlib import asynccontextmanager
from typing import Any
import logging
import os

from fastapi import FastAPI

from src.api.routes import router
from src.services.resource_store import ResourceStore
from src.services.semantic_search import SemanticSearchService

# Basic logging configuration; uvicorn can override, but this sets defaults.
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Initialize and cleanup application resources.

    Creates the ResourceStore and SemanticSearchService on startup,
    making them available to route handlers via app.state.
    """
    # Initialize on startup
    app.state.resource_store = ResourceStore()
    app.state.semantic_search = SemanticSearchService(resource_store=app.state.resource_store)

    # Compute and cache startup health snapshot (no per-request checks)
    status, message = app.state.semantic_search.get_health_status()
    if status == "healthy":
        ollama = "connected"
    elif status == "degraded":
        ollama = "model_not_running"
    else:
        ollama = "disconnected"
    app.state.health_snapshot = {
        "status": status,
        "ollama": ollama,
        "ollama_message": message,
        "model_name": app.state.semantic_search.model,
        "resources_loaded": app.state.resource_store.count(),
    }

    logger.info(
        "Startup health: status=%s ollama=%s resources=%d model=%s",
        app.state.health_snapshot["status"],
        app.state.health_snapshot["ollama"],
        app.state.health_snapshot["resources_loaded"],
        app.state.health_snapshot["model_name"],
    )

    yield

    # Cleanup on shutdown (if needed)
    pass


app = FastAPI(
    title="Smart Tag-Based Resource Fetcher API",
    description=(
        "A FastAPI application that uses DSPy with Ollama for semantic tag-based search "
        "across in-memory resources. Supports synonym matching (e.g., 'home' finds 'house', 'residence')."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
