"""Request and response schemas for the smart-fetcher API."""

from pydantic import BaseModel, Field, field_validator

from src.models.resource import Resource


class SearchResponse(BaseModel):
    """Response wrapper for tag search results.

    Attributes:
        results: List of matching resources.
        count: Number of results returned.
        query: The original search tag (echoed back).
    """

    results: list[Resource] = Field(default_factory=list, description="Matching resources")
    count: int = Field(..., ge=0, description="Number of results")
    query: str = Field(..., description="Original search tag")

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Cozy Cottage",
                        "description": "A warm family dwelling in the countryside.",
                        "search_tag": "home",
                    }
                ],
                "count": 1,
                "query": "house",
            }
        }
    }


class ResourceResponse(BaseModel):
    """Response wrapper for single resource retrieval.

    Attributes:
        resource: The requested resource.
    """

    resource: Resource = Field(..., description="The requested resource")


class ListResponse(BaseModel):
    """Response wrapper for listing all resources.

    Attributes:
        resources: All resources in the system.
        count: Total number of resources.
    """

    resources: list[Resource] = Field(..., description="All resources")
    count: int = Field(..., ge=0, description="Total count")


class ErrorResponse(BaseModel):
    """Standardized error response format.

    Attributes:
        error: Human-readable error message.
        code: Machine-readable error code.
        query: The input that caused the error.
    """

    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    query: str = Field(..., description="Input that caused the error")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Resource not found",
                "code": "RESOURCE_NOT_FOUND",
                "query": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Overall health status ('healthy', 'degraded', or 'unhealthy').
        ollama: Ollama connection status ('connected', 'model_not_running', 'disconnected').
        ollama_message: Detailed message about Ollama/model status.
        model_name: Configured Ollama model name verified at startup.
        resources_loaded: Number of resources in memory.
    """

    status: str = Field(..., description="Overall health status")
    ollama: str = Field(..., description="Ollama connection status")
    ollama_message: str = Field(
        ...,
        description="Detailed status message about Ollama and model availability",
    )
    model_name: str = Field(..., description="Configured model name")
    resources_loaded: int = Field(..., ge=0, description="Number of resources loaded")


class ResourceItem(BaseModel):
    """Individual resource item for NL search results.

    Attributes:
        uuid: Canonical resource identifier.
        name: Resource title.
        summary: Brief description (1-2 sentences).
        link: Internal deep link of the form /resources/{uuid}.
        tags: Optional list of associated tags for traceability.
    """

    uuid: str = Field(..., description="Canonical resource identifier (UUID)")
    name: str = Field(..., description="Resource title")
    summary: str = Field(..., description="Brief description (1-2 sentences)")
    link: str = Field(..., description="Internal deep link /resources/{uuid}")
    tags: list[str] = Field(default_factory=list, description="Associated tags for traceability")

    @field_validator("link")
    @classmethod
    def validate_link_format(cls, v: str) -> str:
        """Ensure link follows /resources/{uuid} pattern."""
        if not v.startswith("/resources/"):
            raise ValueError("Link must start with /resources/")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Hiking Basics",
                "summary": "Starter guide for safe hiking in various terrains.",
                "link": "/resources/550e8400-e29b-41d4-a716-446655440000",
                "tags": ["hiking", "outdoor"],
            }
        }
    }


class NLSearchResponse(BaseModel):
    """Response wrapper for natural language search results.

    Attributes:
        results: List of matching resource items.
        count: Number of results returned.
        query: The original natural language query (echoed back).
        message: Optional message for no-match or ambiguity scenarios.
        candidate_tags: Optional list of suggested tags for refinement.
    """

    results: list[ResourceItem] = Field(default_factory=list, description="Matching resource items")
    count: int = Field(..., ge=0, description="Number of results")
    query: str = Field(..., description="Original natural language query")
    message: str | None = Field(None, description="Optional message for user guidance")
    candidate_tags: list[str] = Field(
        default_factory=list, description="Suggested tags for refinement"
    )
    reasoning: str = Field(
        default="",
        description="DSPy extractor explanation of why extracted tags match the query",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Hiking Basics",
                        "summary": "Starter guide for safe hiking.",
                        "link": "/resources/550e8400-e29b-41d4-a716-446655440000",
                        "tags": ["hiking"],
                    }
                ],
                "count": 1,
                "query": "show me resources that help me improve my hiking habits",
                "reasoning": "The query asks for resources to improve hiking habits, which directly matches the hiking tag.",
            }
        }
    }
