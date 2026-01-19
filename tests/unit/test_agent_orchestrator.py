"""Unit tests for ReACT agent orchestrator."""

from unittest.mock import MagicMock, patch

import pytest

from src.api.schemas import AgentErrorCode
from src.services.agent.react_agent import ReACTAgent
from src.services.nl_search_service import NLSearchService
from src.utils.link_verifier import LinkVerifier


@pytest.fixture
def mock_nl_search_service() -> MagicMock:
    """Create mock NL search service."""
    mock = MagicMock(spec=NLSearchService)
    return mock


@pytest.fixture
def mock_link_verifier() -> MagicMock:
    """Create mock link verifier."""
    mock = MagicMock(spec=LinkVerifier)
    return mock


@pytest.fixture
def agent(mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock) -> ReACTAgent:
    """Create ReACT agent with mocked dependencies."""
    with patch("dspy.LM"), patch("dspy.configure"), patch("dspy.ReAct"):
        agent = ReACTAgent(
            nl_search_service=mock_nl_search_service,
            link_verifier=mock_link_verifier,
        )
        agent.lm = MagicMock()  # Mock the LM
        agent.react_agent = MagicMock()  # Mock the ReAct agent
        return agent


def test_agent_initialization(agent: ReACTAgent) -> None:
    """Test agent initializes correctly."""
    assert agent is not None
    assert agent.nl_search_service is not None
    assert agent.link_verifier is not None


def test_nl_search_tool_success(agent: ReACTAgent, mock_nl_search_service: MagicMock) -> None:
    """Test NL search tool returns results successfully."""
    # Mock search results
    from src.api.schemas import ResourceItem

    mock_item = ResourceItem(
        uuid="test-uuid",
        name="Test Resource",
        summary="Test summary",
        link="/resources/test-uuid",
        tags=["test"],
    )
    mock_nl_search_service.search.return_value = ([mock_item], None, [], "test reasoning")

    # Call tool directly
    agent.current_session_id = "test-session"
    result = agent._nl_search_tool("test query")

    # Verify
    assert "Test Resource" in result
    assert "Test summary" in result


def test_nl_search_tool_error(agent: ReACTAgent, mock_nl_search_service: MagicMock) -> None:
    """Test NL search tool handles errors gracefully."""
    # Mock error
    mock_nl_search_service.search.side_effect = Exception("Search failed")

    # Call tool directly
    agent.current_session_id = "test-session"
    result = agent._nl_search_tool("test query")

    # Verify error handling
    assert "Error" in result
    assert "Search failed" in result


def test_validate_resource_tool_success(agent: ReACTAgent, mock_link_verifier: MagicMock) -> None:
    """Test resource validation tool validates successfully."""
    # Mock validation
    mock_link_verifier.verify_link.return_value = True

    # Call tool directly
    agent.current_session_id = "test-session"
    result = agent._validate_resource_tool("/resources/test-uuid")

    # Verify - now returns bool instead of string
    assert result is True
    assert isinstance(result, bool)


def test_validate_resource_tool_invalid(agent: ReACTAgent, mock_link_verifier: MagicMock) -> None:
    """Test resource validation tool detects invalid resources."""
    # Mock validation
    mock_link_verifier.verify_link.return_value = False

    # Call tool
    result = agent._validate_resource_tool("/resources/bad-uuid")

    # Verify - now returns bool instead of string
    assert result is False
    assert isinstance(result, bool)


def test_validate_resource_tool_returns_bool(
    agent: ReACTAgent, mock_link_verifier: MagicMock
) -> None:
    """Test that validate_resource_tool returns boolean instead of string.

    US1: After modification, _validate_resource_tool should return bool
    for cleaner filtering logic.
    """
    # Mock validation - valid case
    mock_link_verifier.verify_link.return_value = True
    agent.current_session_id = "test-session"

    result = agent._validate_resource_tool("/resources/valid-uuid")

    # Should return True (boolean)
    assert isinstance(result, bool)
    assert result is True

    # Mock validation - invalid case
    mock_link_verifier.verify_link.return_value = False

    result = agent._validate_resource_tool("/resources/invalid-uuid")

    # Should return False (boolean)
    assert isinstance(result, bool)
    assert result is False


def test_agent_run_no_lm_available(
    mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test agent returns error when LM is unavailable."""
    with patch("dspy.LM", side_effect=Exception("LM unavailable")), patch("dspy.ReAct"):
        agent = ReACTAgent(
            nl_search_service=mock_nl_search_service,
            link_verifier=mock_link_verifier,
        )

        # Run agent
        result = agent.run("test query")

        # Verify error response
        assert "error" in result
        assert result["code"] == AgentErrorCode.INTERNAL_ERROR
        assert "unavailable" in result["error"].lower()


def test_agent_run_no_results(agent: ReACTAgent, mock_nl_search_service: MagicMock) -> None:
    """Test agent handles no search results gracefully."""
    # Mock ReAct to raise an exception about no resources
    agent.react_agent.side_effect = Exception("no resources found")

    # Run agent
    result = agent.run("test query")

    # Verify limitation message
    assert "answer" in result
    assert "couldn't find sufficient information" in result["answer"].lower()
    assert result["meta"]["experimental"] is True


def test_agent_run_with_results(agent: ReACTAgent, mock_nl_search_service: MagicMock) -> None:
    """Test agent generates answer with search results."""
    # Mock ReAct prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Here is a test answer about hiking."
    agent.react_agent.return_value = mock_prediction

    # Mock search for resources
    from src.api.schemas import ResourceItem

    mock_item = ResourceItem(
        uuid="test-uuid",
        name="Test Resource",
        summary="Test summary about hiking",
        link="/resources/test-uuid",
        tags=["hiking"],
    )
    mock_nl_search_service.search.return_value = ([mock_item], None, [], "test reasoning")

    # Run agent
    result = agent.run("What is hiking?")

    # Verify answer
    assert "answer" in result
    assert result["answer"] == "Here is a test answer about hiking."
    assert result["query"] == "What is hiking?"
    assert result["meta"]["experimental"] is True


def test_agent_run_with_resources(
    agent: ReACTAgent, mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test agent includes resources when requested."""
    from src.api.schemas import ResourceItem

    # Mock ReAct prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Here is information about hiking."
    agent.react_agent.return_value = mock_prediction

    # Mock search results for resources
    mock_item = ResourceItem(
        uuid="test-uuid",
        name="Hiking Guide",
        summary="Complete hiking guide",
        link="/resources/test-uuid",
        tags=["hiking"],
    )
    mock_nl_search_service.search.return_value = ([mock_item], None, [], "test reasoning")

    # Mock link validation
    mock_link_verifier.verify_link.return_value = True

    # Run agent with sources
    result = agent.run("What is hiking?", include_sources=True)

    # Verify resources
    assert "resources" in result
    assert len(result["resources"]) == 1
    assert result["resources"][0]["title"] == "Hiking Guide"
    assert result["resources"][0]["url"] == "/resources/test-uuid"


def test_agent_run_resources_only_valid(
    agent: ReACTAgent, mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test agent only includes validated resources."""
    from src.api.schemas import ResourceItem

    # Mock ReAct prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer"
    agent.react_agent.return_value = mock_prediction

    # Mock search results with two items
    mock_item1 = ResourceItem(
        uuid="test-uuid-1",
        name="Valid Resource",
        summary="Valid summary",
        link="/resources/test-uuid-1",
        tags=["test"],
    )
    mock_item2 = ResourceItem(
        uuid="test-uuid-2",
        name="Invalid Resource",
        summary="Invalid summary",
        link="/resources/bad-uuid",
        tags=["test"],
    )
    mock_nl_search_service.search.return_value = (
        [mock_item1, mock_item2],
        None,
        [],
        "test reasoning",
    )

    # Mock link validation - first valid, second invalid
    mock_link_verifier.verify_link.side_effect = [True, False]

    # Run agent with sources
    result = agent.run("test query", include_sources=True)

    # Verify only valid resource included
    assert "resources" in result
    assert len(result["resources"]) == 1
    assert result["resources"][0]["title"] == "Valid Resource"


def test_logging_failure_suppressed(
    agent: ReACTAgent, mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test that logging failures do not block resource processing.

    US2-AC4: Per FR-009, logging failures must be suppressed and not
    affect resource filtering or response generation.
    """
    from unittest.mock import patch

    from src.api.schemas import ResourceItem

    # Mock ReAct prediction
    mock_prediction = MagicMock()
    mock_prediction.answer = "Test answer"
    agent.react_agent.return_value = mock_prediction

    # Mock search results
    mock_item = ResourceItem(
        uuid="test-uuid",
        name="Test Resource",
        summary="Test summary",
        link="/resources/test-uuid",
        tags=["test"],
    )
    mock_nl_search_service.search.return_value = (
        [mock_item],
        None,
        [],
        "test reasoning",
    )

    # Mock link validation to fail (triggers hallucination logging)
    mock_link_verifier.verify_link.return_value = False

    # Mock the logger to raise an exception when logging
    import logging

    test_logger = logging.getLogger("src.services.agent.react_agent")
    with patch.object(test_logger, "warning", side_effect=Exception("Logging system failure")):
        # Run agent with sources - should not raise exception despite logging failure
        result = agent.run("test query", include_sources=True)

        # Should return answer with empty resources (triggering 404 in routes)
        # But the logging exception should not propagate
        assert "answer" in result
        # Resources should be empty since all validation failed
        assert "resources" not in result or len(result.get("resources", [])) == 0


def test_cache_enabled_passed_to_dspy_lm(
    mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test that cache=True is passed to dspy.LM when cache is enabled."""
    with (
        patch("src.services.agent.react_agent.settings") as mock_settings,
        patch("dspy.LM") as mock_lm,
        patch("dspy.configure"),
        patch("dspy.ReAct"),
    ):
        mock_settings.dspy_cache_enabled = True
        mock_settings.ollama_model = "gpt-oss:20b"
        mock_settings.ollama_host = "http://localhost:11434"

        _ = ReACTAgent(
            nl_search_service=mock_nl_search_service,
            link_verifier=mock_link_verifier,
        )

        # Verify dspy.LM was called with cache=True
        mock_lm.assert_called_once()
        call_kwargs = mock_lm.call_args.kwargs
        assert call_kwargs["cache"] is True


def test_cache_disabled_passed_to_dspy_lm(
    mock_nl_search_service: MagicMock, mock_link_verifier: MagicMock
) -> None:
    """Test that cache=False is passed to dspy.LM when cache is disabled."""
    with (
        patch("src.services.agent.react_agent.settings") as mock_settings,
        patch("dspy.LM") as mock_lm,
        patch("dspy.configure"),
        patch("dspy.ReAct"),
    ):
        mock_settings.dspy_cache_enabled = False
        mock_settings.ollama_model = "gpt-oss:20b"
        mock_settings.ollama_host = "http://localhost:11434"

        _ = ReACTAgent(
            nl_search_service=mock_nl_search_service,
            link_verifier=mock_link_verifier,
        )

        # Verify dspy.LM was called with cache=False
        mock_lm.assert_called_once()
        call_kwargs = mock_lm.call_args.kwargs
        assert call_kwargs["cache"] is False
