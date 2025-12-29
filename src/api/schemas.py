"""Request and response schemas for the smart-fetcher API."""

import os

from pydantic import BaseModel, Field, field_validator

from src.models.resource import Resource

# Agent Configuration Constants
AGENT_TIMEOUT_SEC = int(os.getenv("AGENT_TIMEOUT_SEC", "5"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "1024"))


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


# Agent Error Codes
class AgentErrorCode:
    """Error codes for agent endpoint."""

    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class Citation(BaseModel):
    """Citation for a validated resource.

    Attributes:
        title: Resource title.
        url: Resource URL (must pass validation).
        summary: Optional brief description.
    """

    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Resource URL (validated)")
    summary: str | None = Field(None, description="Brief description")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Hiking Safety Guide",
                "url": "https://example.com/hiking-guide",
                "summary": "Comprehensive guide to safe hiking practices",
            }
        }
    }


class AgentRequest(BaseModel):
    """Request for the experimental agent endpoint.

    Attributes:
        query: Natural language user query.
        include_sources: Whether to include validated citations.
        max_tokens: Safety cap for response length.
    """

    query: str = Field(..., min_length=1, max_length=4000, description="User query")
    include_sources: bool = Field(default=False, description="Include validated citations")
    max_tokens: int = Field(
        default=AGENT_MAX_TOKENS, ge=128, le=4096, description="Max response tokens"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What is DSPy and how does it help with LLM tooling?",
                "include_sources": False,
                "max_tokens": 1024,
            }
        }
    }


class AgentMeta(BaseModel):
    """Metadata for agent responses.

    Attributes:
        experimental: Indicates experimental status.
    """

    experimental: bool = Field(default=True, description="Experimental status indicator")


class AgentAnswer(BaseModel):
    """Agent response without citations.

    Attributes:
        answer: The agent's final answer.
        query: Original query echoed back.
        meta: Response metadata.
    """

    answer: str = Field(..., description="Agent's final answer")
    query: str = Field(..., description="Original query")
    meta: AgentMeta = Field(default_factory=AgentMeta, description="Response metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "DSPy is a framework for programming with language models...",
                "query": "What is DSPy?",
                "meta": {"experimental": True},
            }
        }
    }


class AgentAnswerWithCitations(AgentAnswer):
    """Agent response with validated citations.

    Attributes:
        citations: List of validated resource citations.
    """

    citations: list[Citation] = Field(default_factory=list, description="Validated citations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "DSPy is a framework for programming with language models...",
                "query": "What is DSPy?",
                "citations": [
                    {
                        "title": "DSPy Documentation",
                        "url": "https://dspy.ai",
                        "summary": "Official DSPy documentation",
                    }
                ],
                "meta": {"experimental": True},
            }
        }
    }


class AgentErrorResponse(BaseModel):
    """Error response for agent endpoint.

    Attributes:
        error: Human-readable error message.
        code: Machine-readable error code (TOOL_TIMEOUT, INTERNAL_ERROR).
        query: Original query that caused the error.
    """

    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    query: str = Field(..., description="Original query")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Agent execution timed out after 5 seconds",
                "code": "TOOL_TIMEOUT",
                "query": "What is DSPy?",
            }
        }
    }
