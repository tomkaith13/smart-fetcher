"""Request and response schemas for the smart-fetcher API."""

from pydantic import BaseModel, Field

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
        status: Overall health status.
        ollama: Ollama connection status.
        resources_loaded: Number of resources in memory.
    """

    status: str = Field(..., description="Overall health status")
    ollama: str = Field(default="unknown", description="Ollama connection status")
    resources_loaded: int = Field(default=0, ge=0, description="Number of resources loaded")
