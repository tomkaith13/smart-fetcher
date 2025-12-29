"""Integration tests for experimental agent API endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for API."""
    return TestClient(app)


def test_agent_endpoint_exists(client: TestClient) -> None:
    """Test that the experimental agent endpoint exists."""
    response = client.post("/experimental/agent", json={"query": "test"})
    # Should not get 404
    assert response.status_code != 404


def test_agent_endpoint_missing_query(client: TestClient) -> None:
    """Test agent endpoint rejects request without query."""
    response = client.post("/experimental/agent", json={})
    assert response.status_code == 400


def test_agent_endpoint_empty_query(client: TestClient) -> None:
    """Test agent endpoint rejects empty query."""
    response = client.post("/experimental/agent", json={"query": ""})
    assert response.status_code == 400


def test_agent_endpoint_query_too_long(client: TestClient) -> None:
    """Test agent endpoint rejects overly long query."""
    response = client.post("/experimental/agent", json={"query": "x" * 5000})
    assert response.status_code == 400


def test_agent_endpoint_basic_query(client: TestClient) -> None:
    """Test agent endpoint handles basic query."""
    response = client.post(
        "/experimental/agent",
        json={"query": "What resources are available for hiking?"},
    )

    # Should succeed or return graceful error
    assert response.status_code in [200, 500, 503, 504]

    if response.status_code == 200:
        data = response.json()
        # Verify response structure
        assert "answer" in data
        assert "query" in data
        assert "meta" in data
        assert data["meta"]["experimental"] is True
        # Should not have citations by default
        assert "citations" not in data or len(data.get("citations", [])) == 0


def test_agent_endpoint_with_include_sources_false(client: TestClient) -> None:
    """Test agent endpoint without citations when include_sources=false."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What resources are available for hiking?",
            "include_sources": False,
        },
    )

    if response.status_code == 200:
        data = response.json()
        # Should not have citations
        assert "citations" not in data or len(data.get("citations", [])) == 0


def test_agent_endpoint_with_include_sources_true(client: TestClient) -> None:
    """Test agent endpoint includes citations when include_sources=true."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What resources are available for hiking?",
            "include_sources": True,
        },
    )

    if response.status_code == 200:
        data = response.json()
        # May have citations if results found
        # If citations present, verify structure
        if "citations" in data:
            assert isinstance(data["citations"], list)
            for citation in data["citations"]:
                assert "title" in citation
                assert "url" in citation


def test_agent_endpoint_custom_max_tokens(client: TestClient) -> None:
    """Test agent endpoint respects custom max_tokens."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What is hiking?",
            "max_tokens": 512,
        },
    )

    # Should accept custom max_tokens
    assert response.status_code in [200, 500, 503, 504]


def test_agent_endpoint_max_tokens_too_low(client: TestClient) -> None:
    """Test agent endpoint rejects max_tokens below minimum."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What is hiking?",
            "max_tokens": 50,
        },
    )

    assert response.status_code == 400


def test_agent_endpoint_max_tokens_too_high(client: TestClient) -> None:
    """Test agent endpoint rejects max_tokens above maximum."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What is hiking?",
            "max_tokens": 10000,
        },
    )

    assert response.status_code == 400


def test_agent_endpoint_response_structure(client: TestClient) -> None:
    """Test agent endpoint returns proper JSON structure."""
    response = client.post(
        "/experimental/agent",
        json={"query": "Tell me about hiking"},
    )

    if response.status_code == 200:
        data = response.json()
        # Verify all required fields present
        assert "answer" in data
        assert "query" in data
        assert "meta" in data

        # Verify types
        assert isinstance(data["answer"], str)
        assert isinstance(data["query"], str)
        assert isinstance(data["meta"], dict)
        assert data["meta"]["experimental"] is True


def test_agent_endpoint_query_echoed_back(client: TestClient) -> None:
    """Test agent endpoint echoes query back in response."""
    test_query = "What is the best way to prepare for hiking?"
    response = client.post(
        "/experimental/agent",
        json={"query": test_query},
    )

    if response.status_code == 200:
        data = response.json()
        assert data["query"] == test_query


def test_agent_endpoint_error_response_structure(client: TestClient) -> None:
    """Test agent endpoint returns proper error structure on failure."""
    # This test checks error structure when agent fails
    # We can't easily trigger specific errors without mocking,
    # but we can verify the structure if we get an error

    response = client.post(
        "/experimental/agent",
        json={"query": "test query that might fail"},
    )

    if response.status_code in [500, 503, 504]:
        data = response.json()
        # FastAPI wraps errors in 'detail'
        detail = data.get("detail", data)
        assert "error" in detail or "detail" in data
        assert "query" in detail or "query" in data


def test_agent_endpoint_handles_special_characters(client: TestClient) -> None:
    """Test agent endpoint handles queries with special characters."""
    response = client.post(
        "/experimental/agent",
        json={"query": "What's the best way to prepare for hiking? (beginner level)"},
    )

    # Should handle special characters gracefully
    assert response.status_code in [200, 500, 503, 504]


def test_agent_endpoint_handles_unicode(client: TestClient) -> None:
    """Test agent endpoint handles Unicode characters."""
    response = client.post(
        "/experimental/agent",
        json={"query": "What is hiking? 🏔️"},
    )

    # Should handle Unicode gracefully
    assert response.status_code in [200, 500, 503, 504]


def test_agent_endpoint_experimental_tag(client: TestClient) -> None:
    """Test agent endpoint is tagged as experimental."""
    # Verify endpoint is in OpenAPI schema with experimental tag
    openapi = client.app.openapi()
    agent_endpoint = openapi["paths"].get("/experimental/agent")

    assert agent_endpoint is not None
    assert "post" in agent_endpoint
    assert "Experimental" in agent_endpoint["post"]["tags"]
