"""Shared test fixtures for smart-fetcher tests."""

from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.models.resource import Resource
from src.services.resource_store import ResourceStore


@pytest.fixture
def sample_resources() -> list[Resource]:
    """Create a small set of sample resources for testing."""
    return [
        Resource(
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Cozy Family Home",
            description="A warm dwelling perfect for families.",
            search_tag="home",
        ),
        Resource(
            uuid="550e8400-e29b-41d4-a716-446655440002",
            name="Modern Apartment",
            description="Urban living at its finest.",
            search_tag="residence",
        ),
        Resource(
            uuid="550e8400-e29b-41d4-a716-446655440003",
            name="Sports Car",
            description="High performance vehicle for enthusiasts.",
            search_tag="car",
        ),
        Resource(
            uuid="550e8400-e29b-41d4-a716-446655440004",
            name="Electric Vehicle",
            description="Eco-friendly transportation option.",
            search_tag="automobile",
        ),
        Resource(
            uuid="550e8400-e29b-41d4-a716-446655440005",
            name="Laptop Computer",
            description="Portable computing device for work and play.",
            search_tag="technology",
        ),
    ]


@pytest.fixture
def resource_store(sample_resources: list[Resource]) -> ResourceStore:
    """Create a ResourceStore with sample resources."""
    return ResourceStore(resources=sample_resources)


@pytest.fixture
def full_resource_store() -> ResourceStore:
    """Create a ResourceStore with the full 100 deterministic resources."""
    return ResourceStore()


@pytest.fixture
def mock_ollama_response() -> MagicMock:
    """Create a mock response for Ollama LLM calls."""
    mock = MagicMock()
    mock.matching_uuids = [
        "550e8400-e29b-41d4-a716-446655440001",
        "550e8400-e29b-41d4-a716-446655440002",
    ]
    return mock


@pytest.fixture
def mock_dspy_lm() -> Generator[MagicMock]:
    """Mock the DSPy LM to avoid actual Ollama calls in tests."""
    with patch("dspy.LM") as mock_lm:
        mock_instance = MagicMock()
        mock_lm.return_value = mock_instance
        yield mock_lm


@pytest.fixture
def mock_semantic_search(mock_ollama_response: MagicMock) -> Generator[MagicMock]:
    """Mock the SemanticSearchService to return predictable results."""
    with patch("src.services.semantic_search.SemanticSearchService") as mock_service:
        mock_instance = MagicMock()
        mock_instance.find_matching = MagicMock(
            return_value=[
                Resource(
                    uuid="550e8400-e29b-41d4-a716-446655440001",
                    name="Cozy Family Home",
                    description="A warm dwelling perfect for families.",
                    search_tag="home",
                ),
                Resource(
                    uuid="550e8400-e29b-41d4-a716-446655440002",
                    name="Modern Apartment",
                    description="Urban living at its finest.",
                    search_tag="residence",
                ),
            ]
        )
        mock_service.return_value = mock_instance
        yield mock_service


@pytest.fixture
def test_client() -> Generator[TestClient]:
    """Create a test client for the FastAPI app with mocked dependencies."""
    # Import here to avoid circular imports and allow mocking
    from src.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Create an async test client for the FastAPI app."""
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def mock_ollama_unavailable() -> Generator[MagicMock]:
    """Mock Ollama being unavailable for error testing."""
    with patch("src.services.semantic_search.SemanticSearchService") as mock_service:
        mock_instance = MagicMock()
        mock_instance.find_matching = MagicMock(
            side_effect=ConnectionError("Ollama service unavailable")
        )
        mock_instance.check_connection = MagicMock(return_value=False)
        mock_service.return_value = mock_instance
        yield mock_service


def create_mock_search_service(
    matching_resources: list[Resource] | None = None,
    is_connected: bool = True,
) -> Any:
    """Factory to create mock search services with custom behavior.

    Args:
        matching_resources: Resources to return from find_matching.
        is_connected: Whether to simulate Ollama being connected.

    Returns:
        Configured mock SemanticSearchService.
    """
    mock_service = MagicMock()

    if matching_resources is None:
        matching_resources = []

    if is_connected:
        mock_service.find_matching = MagicMock(return_value=matching_resources)
        mock_service.check_connection = MagicMock(return_value=True)
    else:
        mock_service.find_matching = MagicMock(
            side_effect=ConnectionError("Ollama service unavailable")
        )
        mock_service.check_connection = MagicMock(return_value=False)

    return mock_service
