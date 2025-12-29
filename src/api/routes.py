"""API route definitions for smart-fetcher."""

import re
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from src.api.schemas import (
    ErrorResponse,
    HealthResponse,
    ListResponse,
    NLSearchResponse,
    ResourceResponse,
    SearchResponse,
)

router = APIRouter()

# UUID regex pattern (accepts any valid UUID format, not just v4)
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    tags=["Search"],
    summary="Search resources by semantic tag",
    description=(
        "Accepts a search tag and returns all resources whose tags are semantically "
        "related. Uses DSPy + Ollama for synonym/concept matching."
    ),
)
async def search_by_tag(
    request: Request,
    tag: Annotated[
        str | None,
        Query(description="The tag to search for (e.g., 'home', 'car', 'technology')"),
    ] = None,
) -> SearchResponse:
    """Search for resources by semantic tag matching."""
    # Validate tag presence
    if tag is None or not tag.strip():
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Tag parameter is required",
                code="MISSING_TAG",
                query=tag or "",
            ).model_dump(),
        )

    tag = tag.strip()

    # Validate tag length
    if len(tag) > 100:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Tag exceeds maximum length of 100 characters",
                code="TAG_TOO_LONG",
                query=tag[:50] + "...",
            ).model_dump(),
        )

    # Perform semantic search
    try:
        semantic_search = request.app.state.semantic_search
        matching_resources = semantic_search.find_matching(tag)

        return SearchResponse(
            results=matching_resources,
            count=len(matching_resources),
            query=tag,
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error="Semantic matching service is unavailable",
                code="SERVICE_UNAVAILABLE",
                query=tag,
            ).model_dump(),
        ) from e


@router.get(
    "/resources/{uuid}",
    response_model=ResourceResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid UUID format"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
    },
    tags=["Resources"],
    summary="Retrieve a resource by UUID",
    description="Returns a single resource by its unique identifier.",
)
async def get_resource_by_uuid(request: Request, uuid: str) -> ResourceResponse:
    """Retrieve a specific resource by its UUID."""
    # Validate UUID format
    if not UUID_PATTERN.match(uuid):
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Invalid UUID format",
                code="INVALID_UUID",
                query=uuid,
            ).model_dump(),
        )

    # Look up resource
    resource_store = request.app.state.resource_store
    resource = resource_store.get_by_uuid(uuid)

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="Resource not found",
                code="RESOURCE_NOT_FOUND",
                query=uuid,
            ).model_dump(),
        )

    return ResourceResponse(resource=resource)


@router.get(
    "/resources",
    response_model=ListResponse,
    tags=["Resources"],
    summary="List all resources",
    description="Returns all 100 resources in the system.",
)
async def list_all_resources(request: Request) -> ListResponse:
    """List all resources in the system."""
    resource_store = request.app.state.resource_store
    resources = resource_store.get_all()

    return ListResponse(
        resources=resources,
        count=len(resources),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Returns the health status of the API and its dependencies.",
)
async def health_check(request: Request, response: Response) -> HealthResponse:
    """Return startup-cached health snapshot without live checks."""
    snapshot = request.app.state.health_snapshot
    response.status_code = 503 if snapshot["status"] == "unhealthy" else 200
    return HealthResponse(**snapshot)


@router.get(
    "/nl/search",
    response_model=NLSearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    tags=["NL Search"],
    summary="Natural language search for resources",
    description=(
        "Accepts a natural language query, extracts relevant domain tags using DSPy + Ollama, "
        "maps tags to canonical resource UUIDs, and returns verified internal deep links. "
        "Responses are JSON-wrapped with results/count/query structure."
    ),
)
async def nl_search(
    request: Request,
    q: Annotated[
        str | None,
        Query(description="Natural language query (e.g., 'show me resources for hiking')"),
    ] = None,
) -> NLSearchResponse:
    """Execute natural language search for resources."""
    # T014: Validate query presence
    if q is None or not q.strip():
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Query parameter 'q' is required",
                code="MISSING_QUERY",
                query=q or "",
            ).model_dump(),
        )

    query = q.strip()

    # T014: Validate query length
    if len(query) > 1000:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Query exceeds maximum length of 1000 characters",
                code="QUERY_TOO_LONG",
                query=query[:50] + "...",
            ).model_dump(),
        )

    # T015: Call NLSearchService.search()
    try:
        nl_service = request.app.state.nl_search_service
        resource_items, message, candidate_tags, reasoning = nl_service.search(query)

        # T016+T040: Assemble NLSearchResponse with JSON wrapping
        return NLSearchResponse(
            results=resource_items,
            count=len(resource_items),
            query=query,
            message=message,
            candidate_tags=candidate_tags,
            reasoning=reasoning,
        )

    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error="NL search service is unavailable",
                code="SERVICE_UNAVAILABLE",
                query=query,
            ).model_dump(),
        ) from e


@router.post(
    "/experimental/agent",
    response_model=None,
    responses={
        200: {"description": "Final answer from agent"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        504: {"model": ErrorResponse, "description": "Tool timeout or unavailable"},
    },
    tags=["Experimental"],
    summary="Run experimental ReACT agent",
    description=(
        "Experimental endpoint that runs a ReACT-style agent using NL search and "
        "resource validation tools. Returns only the final answer; tool traces are "
        "internal-only. Citations included only when explicitly requested."
    ),
)
async def run_experimental_agent(request: Request) -> dict[str, Any]:
    """Execute experimental agent for single-turn query."""
    from src.api.schemas import AgentErrorCode, AgentRequest

    try:
        # Parse request body
        body = await request.json()
        agent_request = AgentRequest(**body)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=f"Invalid request format: {e}",
                code="INVALID_REQUEST",
                query="",
            ).model_dump(),
        ) from e

    # Get agent from app state
    agent = request.app.state.react_agent

    # Run agent
    result: dict[str, Any] = agent.run(
        query=agent_request.query,
        include_sources=agent_request.include_sources,
        max_tokens=agent_request.max_tokens,
    )

    # Check if result is an error
    if "error" in result:
        status_code = 504 if result["code"] == AgentErrorCode.TOOL_TIMEOUT else 500
        raise HTTPException(status_code=status_code, detail=result)

    return result
