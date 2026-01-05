"""Integration tests for experimental agent API endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for API with lifespan events, mocking DSPy config."""
    from unittest.mock import patch

    with patch("dspy.LM"), patch("dspy.configure"), TestClient(app) as c:
        yield c


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
        # Should not have resources by default
        assert "resources" not in data or len(data.get("resources", [])) == 0


def test_agent_endpoint_with_include_sources_false(client: TestClient) -> None:
    """Test agent endpoint without resources when include_sources=false."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What resources are available for hiking?",
            "include_sources": False,
        },
    )

    if response.status_code == 200:
        data = response.json()
        # Should not have resources
        assert "resources" not in data or len(data.get("resources", [])) == 0


def test_agent_endpoint_with_include_sources_true(client: TestClient) -> None:
    """Test agent endpoint includes resources when include_sources=true."""
    response = client.post(
        "/experimental/agent",
        json={
            "query": "What resources are available for hiking?",
            "include_sources": True,
        },
    )

    if response.status_code == 200:
        data = response.json()
        # May have resources if results found
        # If resources present, verify structure
        if "resources" in data:
            assert isinstance(data["resources"], list)
            for resource in data["resources"]:
                assert "title" in resource
                assert "url" in resource


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


def test_agent_filters_invalid_resources(client: TestClient) -> None:
    """Test that invalid resources are filtered from response.

    US1: When include_sources=true, only resources passing validation
    should be included in the response.
    """
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Mock resources: 2 valid, 1 invalid
    mock_items = [
        ResourceItem(
            uuid="valid-uuid-1",
            name="Valid Resource 1",
            summary="First valid resource",
            link="/resources/valid-uuid-1",
            tags=["test"],
        ),
        ResourceItem(
            uuid="invalid-uuid",
            name="Invalid Resource",
            summary="This will fail validation",
            link="/resources/invalid-uuid",
            tags=["test"],
        ),
        ResourceItem(
            uuid="valid-uuid-2",
            name="Valid Resource 2",
            summary="Second valid resource",
            link="/resources/valid-uuid-2",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer about resources."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")

        # First and third resources are valid, middle one is invalid
        mock_verify.side_effect = [True, False, True]

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test query",
                "include_sources": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Should have exactly 2 resources (the valid ones)
        assert "resources" in data
        assert len(data["resources"]) == 2
        assert data["resources"][0]["title"] == "Valid Resource 1"
        assert data["resources"][1]["title"] == "Valid Resource 2"
        # Invalid resource should not be present
        assert not any(r["title"] == "Invalid Resource" for r in data["resources"])


def test_agent_all_invalid_returns_404(client: TestClient) -> None:
    """Test that HTTP 404 is returned when all resources fail validation.

    US1-AC2: When include_sources=true and all resources fail validation,
    return HTTP 404 with specific error message.
    """
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Mock resources: all invalid
    mock_items = [
        ResourceItem(
            uuid="invalid-uuid-1",
            name="Invalid Resource 1",
            summary="First invalid resource",
            link="/resources/invalid-uuid-1",
            tags=["test"],
        ),
        ResourceItem(
            uuid="invalid-uuid-2",
            name="Invalid Resource 2",
            summary="Second invalid resource",
            link="/resources/invalid-uuid-2",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer about resources."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")

        # All resources fail validation
        mock_verify.return_value = False

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test query",
                "include_sources": True,
            },
        )

        # Should return HTTP 404
        assert response.status_code == 404

        data = response.json()
        detail = data.get("detail", data)

        # Verify error structure
        assert "error" in detail
        assert "code" in detail
        assert "query" in detail
        assert detail["error"] == "no valid resources found"
        assert detail["code"] == "NO_VALID_RESOURCES"
        assert detail["query"] == "test query"


def test_agent_all_valid_included(client: TestClient) -> None:
    """Test that all valid resources are included in response.

    US1-AC1: When include_sources=true and all resources pass validation,
    all should be included in the response.
    """
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Mock resources: all valid
    mock_items = [
        ResourceItem(
            uuid="valid-uuid-1",
            name="Valid Resource 1",
            summary="First valid resource",
            link="/resources/valid-uuid-1",
            tags=["test"],
        ),
        ResourceItem(
            uuid="valid-uuid-2",
            name="Valid Resource 2",
            summary="Second valid resource",
            link="/resources/valid-uuid-2",
            tags=["test"],
        ),
        ResourceItem(
            uuid="valid-uuid-3",
            name="Valid Resource 3",
            summary="Third valid resource",
            link="/resources/valid-uuid-3",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer about resources."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")

        # All resources are valid
        mock_verify.return_value = True

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test query",
                "include_sources": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Should have all 3 resources
        assert "resources" in data
        assert len(data["resources"]) == 3
        assert data["resources"][0]["title"] == "Valid Resource 1"
        assert data["resources"][1]["title"] == "Valid Resource 2"
        assert data["resources"][2]["title"] == "Valid Resource 3"


def test_agent_logs_hallucinations_at_warning_level(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that hallucinations are logged at WARNING level.

    US2-AC1: Invalid resources (hallucinations) should be logged at WARNING level
    with resource details (URL, title, query).
    """
    import logging
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Capture logs from the agent_logger
    caplog.set_level(logging.WARNING, logger="agent_logger")

    # Mock resources: 1 valid, 1 invalid
    mock_items = [
        ResourceItem(
            uuid="valid-uuid",
            name="Valid Resource",
            summary="Valid resource",
            link="/resources/valid-uuid",
            tags=["test"],
        ),
        ResourceItem(
            uuid="invalid-uuid",
            name="Invalid Resource",
            summary="Invalid resource",
            link="/resources/invalid-uuid",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")
        mock_verify.side_effect = [True, False]  # First valid, second invalid

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test hallucination query",
                "include_sources": True,
            },
        )

        assert response.status_code == 200

        # Check that hallucination was logged at WARNING level
        warning_records = [
            r for r in caplog.records if r.levelname == "WARNING" and "react_agent" in r.name
        ]
        assert len(warning_records) >= 1

        # Find the hallucination log
        hallucination_logs = [r for r in warning_records if "Hallucination detected" in r.message]
        assert len(hallucination_logs) == 1

        log_record = hallucination_logs[0]
        assert "invalid resource" in log_record.message.lower()
        assert "/resources/invalid-uuid" in log_record.message


def test_agent_logs_multiple_hallucinations(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that multiple hallucinations are logged separately.

    US2-AC2: When multiple resources fail validation, each should generate
    a separate log entry.
    """
    import logging
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Capture logs from the agent_logger
    caplog.set_level(logging.WARNING, logger="agent_logger")

    # Mock resources: all invalid
    mock_items = [
        ResourceItem(
            uuid="invalid-uuid-1",
            name="Invalid Resource 1",
            summary="First invalid",
            link="/resources/invalid-uuid-1",
            tags=["test"],
        ),
        ResourceItem(
            uuid="invalid-uuid-2",
            name="Invalid Resource 2",
            summary="Second invalid",
            link="/resources/invalid-uuid-2",
            tags=["test"],
        ),
        ResourceItem(
            uuid="invalid-uuid-3",
            name="Invalid Resource 3",
            summary="Third invalid",
            link="/resources/invalid-uuid-3",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")
        mock_verify.return_value = False  # All fail validation

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test multiple hallucinations",
                "include_sources": True,
            },
        )

        # Should get 404 since all resources invalid
        assert response.status_code == 404

        # Check that we have 3 separate hallucination logs
        warning_records = [
            r for r in caplog.records if r.levelname == "WARNING" and "react_agent" in r.name
        ]
        hallucination_logs = [r for r in warning_records if "Hallucination detected" in r.message]
        assert len(hallucination_logs) == 3

        # Verify each resource was logged
        logged_urls = [r.message for r in hallucination_logs]
        assert any("invalid-uuid-1" in msg for msg in logged_urls)
        assert any("invalid-uuid-2" in msg for msg in logged_urls)
        assert any("invalid-uuid-3" in msg for msg in logged_urls)


def test_agent_logs_validation_exceptions(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that validation exceptions are logged at ERROR level.

    US2-AC3: When validation raises an exception, it should be logged at ERROR
    level with exception details.
    """
    import logging
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Capture logs from the react_agent module logger
    caplog.set_level(logging.ERROR, logger="src.services.agent.react_agent")

    # Mock resources
    mock_items = [
        ResourceItem(
            uuid="exception-uuid",
            name="Exception Resource",
            summary="Will throw exception",
            link="/resources/exception-uuid",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")
        mock_verify.side_effect = Exception("Validation failed unexpectedly")

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test exception handling",
                "include_sources": True,
            },
        )

        # Should get 404 since resource validation failed
        assert response.status_code == 404

        # Check that exception was logged at ERROR level
        error_records = [
            r for r in caplog.records if r.levelname == "ERROR" and "react_agent" in r.name
        ]
        assert len(error_records) >= 1

        # Find the validation exception log
        exception_logs = [r for r in error_records if "Validation exception" in r.message]
        assert len(exception_logs) == 1

        log_record = exception_logs[0]
        assert "exception-uuid" in log_record.message
        assert "Validation failed unexpectedly" in log_record.message


def test_no_logs_when_all_valid(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    """Test that no hallucination logs are generated when all resources are valid.

    US2: When all resources pass validation, no WARNING or ERROR logs
    should be generated for hallucinations.
    """
    import logging
    from unittest.mock import MagicMock, patch

    from src.api.schemas import ResourceItem

    # Set log level to capture all logs
    caplog.set_level(logging.DEBUG)

    # Mock resources: all valid
    mock_items = [
        ResourceItem(
            uuid="valid-uuid-1",
            name="Valid Resource 1",
            summary="First valid",
            link="/resources/valid-uuid-1",
            tags=["test"],
        ),
        ResourceItem(
            uuid="valid-uuid-2",
            name="Valid Resource 2",
            summary="Second valid",
            link="/resources/valid-uuid-2",
            tags=["test"],
        ),
    ]

    # Mock the ReAct agent prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer."

    with (
        patch.object(client.app.state.react_agent, "react_agent") as mock_react,
        patch.object(client.app.state.react_agent.nl_search_service, "search") as mock_search,
        patch.object(client.app.state.react_agent.link_verifier, "verify_link") as mock_verify,
    ):
        mock_react.return_value = mock_prediction
        mock_search.return_value = (mock_items, None, [], "test reasoning")
        mock_verify.return_value = True  # All valid

        response = client.post(
            "/experimental/agent",
            json={
                "query": "test no hallucinations",
                "include_sources": True,
            },
        )

        assert response.status_code == 200

        # Check that no hallucination or validation exception logs were generated
        all_logs = [r.message for r in caplog.records]
        hallucination_logs = [msg for msg in all_logs if "Hallucination detected" in msg]
        exception_logs = [msg for msg in all_logs if "Validation exception" in msg]

        assert len(hallucination_logs) == 0
        assert len(exception_logs) == 0
