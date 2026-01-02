"""Contract tests for experimental agent endpoint response schemas."""

import pytest
from pydantic import ValidationError

from src.api.schemas import (
    AgentAnswer,
    AgentAnswerWithResources,
    AgentErrorResponse,
    AgentMeta,
    AgentRequest,
    ResourceCitation,
)


def test_agent_request_valid() -> None:
    """Test AgentRequest validates correctly with required fields."""
    request = AgentRequest(query="What is DSPy?")
    assert request.query == "What is DSPy?"
    assert request.include_sources is False
    assert request.max_tokens == 1024


def test_agent_request_with_sources() -> None:
    """Test AgentRequest with include_sources flag."""
    request = AgentRequest(query="What is DSPy?", include_sources=True)
    assert request.include_sources is True


def test_agent_request_custom_max_tokens() -> None:
    """Test AgentRequest with custom max_tokens."""
    request = AgentRequest(query="What is DSPy?", max_tokens=512)
    assert request.max_tokens == 512


def test_agent_request_empty_query() -> None:
    """Test AgentRequest rejects empty query."""
    with pytest.raises(ValidationError):
        AgentRequest(query="")


def test_agent_request_query_too_long() -> None:
    """Test AgentRequest rejects query exceeding max length."""
    with pytest.raises(ValidationError):
        AgentRequest(query="x" * 5000)


def test_agent_request_max_tokens_too_low() -> None:
    """Test AgentRequest rejects max_tokens below minimum."""
    with pytest.raises(ValidationError):
        AgentRequest(query="test", max_tokens=50)


def test_agent_request_max_tokens_too_high() -> None:
    """Test AgentRequest rejects max_tokens above maximum."""
    with pytest.raises(ValidationError):
        AgentRequest(query="test", max_tokens=10000)


def test_agent_meta() -> None:
    """Test AgentMeta has experimental flag."""
    meta = AgentMeta()
    assert meta.experimental is True


def test_agent_answer_valid() -> None:
    """Test AgentAnswer schema with required fields."""
    answer = AgentAnswer(
        answer="DSPy is a framework for LLM programming.",
        query="What is DSPy?",
    )
    assert answer.answer == "DSPy is a framework for LLM programming."
    assert answer.query == "What is DSPy?"
    assert answer.meta.experimental is True


def test_agent_answer_serialization() -> None:
    """Test AgentAnswer serializes to dict correctly."""
    answer = AgentAnswer(
        answer="DSPy is a framework.",
        query="What is DSPy?",
    )
    data = answer.model_dump()
    assert data["answer"] == "DSPy is a framework."
    assert data["query"] == "What is DSPy?"
    assert data["meta"]["experimental"] is True


def test_resource_citation_valid() -> None:
    """Test ResourceCitation schema with required fields."""
    citation = ResourceCitation(
        title="DSPy Documentation",
        url="https://dspy.ai",
        summary="Official DSPy docs",
    )
    assert citation.title == "DSPy Documentation"
    assert citation.url == "https://dspy.ai"
    assert citation.summary == "Official DSPy docs"


def test_resource_citation_without_summary() -> None:
    """Test ResourceCitation allows None for summary."""
    citation = ResourceCitation(title="DSPy Docs", url="https://dspy.ai")
    assert citation.summary is None


def test_agent_answer_with_resources_valid() -> None:
    """Test AgentAnswerWithResources includes resources list."""
    resources = [
        ResourceCitation(title="DSPy Docs", url="https://dspy.ai", summary="Official docs"),
    ]
    answer = AgentAnswerWithResources(
        answer="DSPy is a framework.",
        query="What is DSPy?",
        resources=resources,
    )
    assert len(answer.resources) == 1
    assert answer.resources[0].title == "DSPy Docs"


def test_agent_answer_with_resources_empty() -> None:
    """Test AgentAnswerWithResources allows empty resources list."""
    answer = AgentAnswerWithResources(
        answer="DSPy is a framework.",
        query="What is DSPy?",
        resources=[],
    )
    assert len(answer.resources) == 0


def test_agent_answer_with_resources_serialization() -> None:
    """Test AgentAnswerWithResources serializes correctly."""
    resources = [
        ResourceCitation(title="DSPy Docs", url="https://dspy.ai"),
    ]
    answer = AgentAnswerWithResources(
        answer="DSPy is a framework.",
        query="What is DSPy?",
        resources=resources,
    )
    data = answer.model_dump()
    assert "resources" in data
    assert len(data["resources"]) == 1
    assert data["resources"][0]["title"] == "DSPy Docs"
    assert data["resources"][0]["url"] == "https://dspy.ai"


def test_agent_error_response_valid() -> None:
    """Test AgentErrorResponse schema."""
    error = AgentErrorResponse(
        error="Agent execution timed out",
        code="TOOL_TIMEOUT",
        query="What is DSPy?",
    )
    assert error.error == "Agent execution timed out"
    assert error.code == "TOOL_TIMEOUT"
    assert error.query == "What is DSPy?"


def test_agent_error_response_serialization() -> None:
    """Test AgentErrorResponse serializes correctly."""
    error = AgentErrorResponse(
        error="Internal error occurred",
        code="INTERNAL_ERROR",
        query="test query",
    )
    data = error.model_dump()
    assert data["error"] == "Internal error occurred"
    assert data["code"] == "INTERNAL_ERROR"
    assert data["query"] == "test query"


def test_contract_compliance_success_no_resources() -> None:
    """Test response matches OpenAPI contract for success without resources."""
    answer = AgentAnswer(
        answer="DSPy is a framework for programming with language models.",
        query="What is DSPy?",
    )
    data = answer.model_dump()

    # Verify required fields per OpenAPI contract
    assert "answer" in data
    assert "query" in data
    assert "meta" in data
    assert data["meta"]["experimental"] is True

    # Verify no resources field
    assert "resources" not in data


def test_contract_compliance_success_with_resources() -> None:
    """Test response matches OpenAPI contract for success with resources."""
    resources = [
        ResourceCitation(title="DSPy Documentation", url="https://dspy.ai", summary="Official docs"),
    ]
    answer = AgentAnswerWithResources(
        answer="DSPy is a framework.",
        query="What is DSPy?",
        resources=resources,
    )
    data = answer.model_dump()

    # Verify required fields per OpenAPI contract
    assert "answer" in data
    assert "query" in data
    assert "meta" in data
    assert "resources" in data
    assert data["meta"]["experimental"] is True
    assert isinstance(data["resources"], list)
    assert len(data["resources"]) == 1


def test_contract_compliance_error_response() -> None:
    """Test error response matches OpenAPI contract."""
    error = AgentErrorResponse(
        error="Tool timeout occurred",
        code="TOOL_TIMEOUT",
        query="test query",
    )
    data = error.model_dump()

    # Verify required fields per OpenAPI contract
    assert "error" in data
    assert "code" in data
    assert "query" in data
    assert data["code"] in ["TOOL_TIMEOUT", "INTERNAL_ERROR"]
