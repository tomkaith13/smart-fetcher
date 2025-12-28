"""Integration tests for the /nl/search API endpoint."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.models.resource import Resource
from src.services.nl_tag_extractor import TagExtractionResult


class TestNLSearchAPIIntegration:
    """Integration tests for the natural language search endpoint."""

    @pytest.fixture
    def client_with_mock_services(self) -> Generator[TestClient]:
        """Create test client with mocked services and resource store."""
        with (
            patch("src.main.SemanticSearchService") as mock_semantic,
            patch("src.main.ResourceStore") as mock_store_class,
            patch("src.main.NLTagExtractor") as mock_extractor_class,
        ):
            # Mock semantic search
            mock_semantic_instance = MagicMock()
            mock_semantic_instance.model = "gpt-oss:20b"
            mock_semantic_instance.get_health_status.return_value = ("healthy", "Ready")
            mock_semantic_instance.check_connection.return_value = True
            mock_semantic.return_value = mock_semantic_instance

            # Mock resource store with sample data
            mock_store = MagicMock()
            mock_store.get_by_tags.return_value = [
                Resource(
                    uuid="550e8400-e29b-41d4-a716-446655440001",
                    name="Hiking Basics",
                    description="Comprehensive guide for safe hiking in various terrains and weather conditions.",
                    search_tag="hiking",
                ),
                Resource(
                    uuid="550e8400-e29b-41d4-a716-446655440002",
                    name="Trail Safety Guide",
                    description="Essential safety tips for trail hiking and wilderness navigation.",
                    search_tag="outdoor",
                ),
            ]
            mock_store.get_unique_tags.return_value = ["hiking", "finance", "health"]
            mock_store.get_by_uuid.return_value = Resource(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                name="Hiking Basics",
                description="Comprehensive guide.",
                search_tag="hiking",
            )
            mock_store_class.return_value = mock_store

            # Mock NL tag extractor with reasoning
            mock_extractor = MagicMock()
            mock_extractor.extract.return_value = TagExtractionResult(
                tags=["hiking"],
                confidence=0.95,
                ambiguous=False,
                reasoning="The query asks about improving hiking habits, which directly matches the hiking tag.",
            )
            mock_extractor_class.return_value = mock_extractor

            from src.main import app

            with TestClient(app) as client:
                # Store mocks for later access
                client.mock_store = mock_store
                client.mock_extractor = mock_extractor
                yield client

    def test_nl_search_valid_query_returns_results_with_reasoning(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test NL search with valid query returns matching resources with reasoning (T022, US1)."""
        response = client_with_mock_services.get(
            "/nl/search?q=show me resources that help me improve my hiking habits"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["count"] >= 1
        assert len(data["results"]) >= 1
        assert data["query"] == "show me resources that help me improve my hiking habits"

        # Verify top-level reasoning (NEW)
        assert "reasoning" in data
        assert data["reasoning"] != ""
        assert isinstance(data["reasoning"], str)

    def test_nl_search_verifies_internal_links(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that all returned links are verified internal deep links (T042, US1)."""
        response = client_with_mock_services.get("/nl/search?q=hiking")

        assert response.status_code == 200
        data = response.json()

        for result in data["results"]:
            # Verify internal deep link format
            assert result["link"].startswith("/resources/")
            # Verify UUID is in the link
            assert result["uuid"] in result["link"]
            # Verify link matches expected format
            expected_link = f"/resources/{result['uuid']}"
            assert result["link"] == expected_link

    def test_nl_search_respects_result_cap(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that NL search respects the default result cap of 5 (US1)."""
        # Mock extractor to return many results
        mock_store = client_with_mock_services.mock_store
        many_resources = [
            Resource(
                uuid=f"550e8400-e29b-41d4-a716-44665544000{i}",
                name=f"Resource {i}",
                description=f"Description for resource {i}",
                search_tag="hiking",
            )
            for i in range(10)
        ]
        mock_store.get_by_tags.return_value = many_resources

        response = client_with_mock_services.get("/nl/search?q=hiking")

        assert response.status_code == 200
        data = response.json()

        # Should cap at 5 results by default
        assert data["count"] <= 5
        assert len(data["results"]) <= 5

    def test_nl_search_no_match_returns_suggestions(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test no-match query returns helpful message with suggestions (T028, US2)."""
        # Mock extractor to return no tags
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=[],
            confidence=0.0,
            ambiguous=False,
            reasoning="",
        )

        response = client_with_mock_services.get("/nl/search?q=xyzzy nonsense query")

        assert response.status_code == 200
        data = response.json()

        # Verify no-match scenario (T028, US2)
        assert data["count"] == 0
        assert data["results"] == []
        assert data["message"] is not None
        assert len(data["candidate_tags"]) >= 2  # At least 2 suggestions

    def test_nl_search_ambiguous_query_returns_refinement_prompt(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test ambiguous query returns candidate tags and refinement message (T033, US3)."""
        # Mock extractor to return ambiguous tags
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=["fitness", "health"],
            confidence=0.7,
            ambiguous=True,
            reasoning="Multiple tags match with similar confidence: fitness and health.",
        )

        mock_store = client_with_mock_services.mock_store
        mock_store.get_by_tags.return_value = [
            Resource(
                uuid="550e8400-e29b-41d4-a716-446655440010",
                name="Exercise Guide",
                description="Fitness and health resource.",
                search_tag="fitness",
            ),
        ]

        response = client_with_mock_services.get("/nl/search?q=exercise")

        assert response.status_code == 200
        data = response.json()

        # Verify ambiguity handling (T033, US3)
        assert data["message"] is not None
        assert "multiple" in data["message"].lower() or "refine" in data["message"].lower()
        assert len(data["candidate_tags"]) >= 2
        # Should still return some results
        assert data["count"] >= 0

    def test_nl_search_preserves_reasoning_from_extractor(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that reasoning from DSPy extractor is preserved in response (NEW)."""
        # Set specific reasoning
        expected_reasoning = "Query mentions hiking which relates to outdoor activities."
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=["hiking"],
            confidence=0.9,
            ambiguous=False,
            reasoning=expected_reasoning,
        )

        response = client_with_mock_services.get("/nl/search?q=hiking tips")

        assert response.status_code == 200
        data = response.json()

        # Verify reasoning is propagated at top-level
        assert data["count"] >= 1
        assert data["reasoning"] == expected_reasoning

    def test_nl_search_empty_reasoning_for_fallback_mode(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that fallback mode returns appropriate reasoning message (NEW)."""
        # Mock fallback extraction (keyword-based)
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=["hiking"],
            confidence=0.5,
            ambiguous=False,
            reasoning="Keyword-based matching (fallback mode)",
        )

        response = client_with_mock_services.get("/nl/search?q=hiking")

        assert response.status_code == 200
        data = response.json()

        # Verify fallback reasoning is present at top-level
        assert "reasoning" in data
        assert data["reasoning"] == "Keyword-based matching (fallback mode)"

    def test_nl_search_returns_truncated_summaries(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that long descriptions are truncated to 200 chars in summaries (US1)."""
        # Mock resource with very long description
        long_desc = "A" * 300
        mock_store = client_with_mock_services.mock_store
        mock_store.get_by_tags.return_value = [
            Resource(
                uuid="550e8400-e29b-41d4-a716-446655440099",
                name="Long Description Resource",
                description=long_desc,
                search_tag="hiking",
            ),
        ]

        response = client_with_mock_services.get("/nl/search?q=hiking")

        assert response.status_code == 200
        data = response.json()

        # Verify summary is truncated
        assert data["count"] == 1
        summary = data["results"][0]["summary"]
        assert len(summary) <= 203  # 200 + "..."
        assert summary.endswith("...")

    def test_nl_search_json_wrapping_consistency(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that response follows JSON wrapping convention (T041, FR-011)."""
        response = client_with_mock_services.get("/nl/search?q=test query")

        assert response.status_code == 200
        data = response.json()

        # Verify JSON wrapping structure
        assert "results" in data
        assert "count" in data
        assert "query" in data
        assert "message" in data
        assert "candidate_tags" in data
        assert "reasoning" in data

        # Verify count matches results length
        assert data["count"] == len(data["results"])

        # Verify query is echoed
        assert data["query"] == "test query"

    def test_nl_search_results_do_not_include_per_item_reasoning(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Ensure no per-item reasoning is present; reasoning is top-level only."""
        response = client_with_mock_services.get(
            "/nl/search?q=show me resources that help me improve my hiking habits"
        )

        assert response.status_code == 200
        data = response.json()

        # Top-level reasoning must be present
        assert "reasoning" in data
        assert isinstance(data["reasoning"], str)

        # Each result item must NOT contain a reasoning field
        for item in data["results"]:
            assert "reasoning" not in item


class TestNLSearchEdgeCases:
    """Integration tests for edge cases and error scenarios."""

    @pytest.fixture
    def client_with_mock_services(self) -> Generator[TestClient]:
        """Create test client with mocked services."""
        with (
            patch("src.main.SemanticSearchService") as mock_semantic,
            patch("src.main.ResourceStore") as mock_store_class,
            patch("src.main.NLTagExtractor") as mock_extractor_class,
        ):
            mock_semantic_instance = MagicMock()
            mock_semantic_instance.model = "gpt-oss:20b"
            mock_semantic_instance.get_health_status.return_value = ("healthy", "Ready")
            mock_semantic_instance.check_connection.return_value = True
            mock_semantic.return_value = mock_semantic_instance

            mock_store = MagicMock()
            mock_store_class.return_value = mock_store

            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            from src.main import app

            with TestClient(app) as client:
                client.mock_store = mock_store
                client.mock_extractor = mock_extractor
                yield client

    def test_nl_search_handles_special_characters_in_query(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that special characters in queries are handled gracefully."""
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=["hiking"],
            confidence=0.8,
            ambiguous=False,
            reasoning="Query processed successfully.",
        )
        client_with_mock_services.mock_store.get_by_tags.return_value = []

        response = client_with_mock_services.get("/nl/search?q=hiking%20%26%20camping%21")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "hiking & camping!"

    def test_nl_search_handles_unicode_in_query(
        self, client_with_mock_services: TestClient
    ) -> None:
        """Test that Unicode characters in queries are handled correctly."""
        client_with_mock_services.mock_extractor.extract.return_value = TagExtractionResult(
            tags=["travel"],
            confidence=0.8,
            ambiguous=False,
            reasoning="Unicode query processed.",
        )
        client_with_mock_services.mock_store.get_by_tags.return_value = []

        response = client_with_mock_services.get("/nl/search?q=café%20☕")

        assert response.status_code == 200
        data = response.json()
        assert "café" in data["query"]
