"""Unit tests for SemanticSearchService."""

from unittest.mock import MagicMock, patch

import pytest

from src.models.resource import Resource
from src.services.resource_store import ResourceStore
from src.services.semantic_search import SemanticResourceFinder, SemanticSearchService


class TestSemanticResourceFinder:
    """Tests for the SemanticResourceFinder DSPy Signature."""

    def test_signature_has_required_fields(self) -> None:
        """Verify the signature has the expected input and output fields."""
        # DSPy Signature fields are defined as annotations
        annotations = SemanticResourceFinder.__annotations__

        # Check input fields
        assert "search_tag" in annotations
        assert "resources_context" in annotations

        # Check output field
        assert "matching_uuids" in annotations


class TestSemanticSearchService:
    """Tests for the SemanticSearchService class."""

    @pytest.fixture
    def mock_resource_store(self, sample_resources: list[Resource]) -> ResourceStore:
        """Create a resource store with sample data."""
        return ResourceStore(resources=sample_resources)

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_returns_resources(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching returns matching resources."""
        # Setup mock to return matching UUIDs
        mock_finder = MagicMock()
        mock_result = MagicMock()
        mock_result.matching_uuids = [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ]
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("home")

        assert len(results) == 2
        assert all(isinstance(r, Resource) for r in results)
        assert results[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        assert results[1].uuid == "550e8400-e29b-41d4-a716-446655440002"

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_empty_results(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching handles no matches gracefully."""
        mock_finder = MagicMock()
        mock_result = MagicMock()
        mock_result.matching_uuids = []
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("xyzzy")

        assert results == []

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_handles_string_response(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching handles JSON string responses from LLM."""
        mock_finder = MagicMock()
        mock_result = MagicMock()
        # LLM might return a JSON string instead of a list
        mock_result.matching_uuids = '["550e8400-e29b-41d4-a716-446655440001"]'
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("home")

        assert len(results) == 1
        assert results[0].uuid == "550e8400-e29b-41d4-a716-446655440001"

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_handles_invalid_uuids(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching ignores invalid UUIDs from LLM."""
        mock_finder = MagicMock()
        mock_result = MagicMock()
        mock_result.matching_uuids = [
            "550e8400-e29b-41d4-a716-446655440001",
            "invalid-uuid-not-in-store",
        ]
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("home")

        # Should only return the valid UUID that exists in store
        assert len(results) == 1
        assert results[0].uuid == "550e8400-e29b-41d4-a716-446655440001"

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_connection_error(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching raises ConnectionError when Ollama unavailable."""
        mock_finder = MagicMock()
        mock_finder.side_effect = Exception("Connection refused")
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)

        with pytest.raises(ConnectionError):
            service.find_matching("home")

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    def test_check_connection_success(
        self,
        mock_get: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_connection returns True when Ollama is reachable."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_connection() is True

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    def test_check_connection_failure(
        self,
        mock_get: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_connection returns False when Ollama is unreachable."""
        mock_get.side_effect = Exception("Connection refused")

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_connection() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_service_uses_environment_config(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that service reads configuration from environment variables."""
        monkeypatch.setenv("OLLAMA_HOST", "http://custom-host:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

        service = SemanticSearchService(resource_store=mock_resource_store)

        assert service.ollama_host == "http://custom-host:11434"
        assert service.model == "custom-model"
