"""Resource model for the smart-fetcher application."""

from pydantic import BaseModel, Field


class Resource(BaseModel):
    """A searchable resource with semantic tag matching capability.

    Attributes:
        uuid: Unique identifier for the resource (UUID v4 format).
        name: Human-readable name for the resource.
        description: Descriptive text explaining the resource.
        search_tag: Categorization label for semantic matching.
    """

    uuid: str = Field(..., description="Unique identifier (UUID v4)")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: str = Field(..., min_length=1, max_length=1000, description="Resource description")
    search_tag: str = Field(..., min_length=1, max_length=100, description="Categorization tag")

    model_config = {
        "json_schema_extra": {
            "example": {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Ergonomic Office Chair",
                "description": "A comfortable chair designed for long work sessions.",
                "search_tag": "work",
            }
        }
    }
