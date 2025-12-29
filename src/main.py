"""FastAPI application entry point for smart-fetcher."""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.api.routes import router
from src.services.agent.react_agent import ReACTAgent
from src.services.nl_search_service import NLSearchService
from src.services.nl_tag_extractor import NLTagExtractor
from src.services.resource_store import ResourceStore
from src.services.semantic_search import SemanticSearchService
from src.utils.link_verifier import LinkVerifier

# Basic logging configuration; uvicorn can override, but this sets defaults.
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# NL Search Configuration
NL_SEARCH_DEFAULT_RESULT_CAP = int(os.getenv("NL_SEARCH_RESULT_CAP", "5"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Initialize and cleanup application resources.

    Creates the ResourceStore and SemanticSearchService on startup,
    making them available to route handlers via app.state.
    """
    # Initialize on startup
    app.state.resource_store = ResourceStore()
    app.state.semantic_search = SemanticSearchService(resource_store=app.state.resource_store)

    # Initialize NL search services
    available_tags = app.state.resource_store.get_unique_tags()
    app.state.nl_tag_extractor = NLTagExtractor(
        available_tags=available_tags,
        lm=app.state.semantic_search.lm,
    )
    app.state.nl_search_service = NLSearchService(
        extractor=app.state.nl_tag_extractor,
        resource_store=app.state.resource_store,
        default_cap=NL_SEARCH_DEFAULT_RESULT_CAP,
    )

    # Initialize experimental ReACT agent
    app.state.link_verifier = LinkVerifier(resource_store=app.state.resource_store)
    app.state.react_agent = ReACTAgent(
        nl_search_service=app.state.nl_search_service,
        link_verifier=app.state.link_verifier,
    )

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
