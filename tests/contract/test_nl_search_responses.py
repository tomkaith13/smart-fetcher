"""Contract tests for /nl/search endpoint response formats."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestNLSearchResponseFormat:
    """Contract tests verifying NLSearchResponse matches OpenAPI spec."""

    @pytest.fixture
    def client_with_mock_nl_search(self) -> Generator[TestClient]:
        """Create test client with mocked NL search service."""
        with (
            patch("src.main.SemanticSearchService") as mock_semantic,
            patch("src.main.NLSearchService") as mock_nl_service_class,
            patch("src.main.NLTagExtractor") as mock_extractor_class,
        ):
            # Mock semantic search service
            mock_semantic_instance = MagicMock()
            mock_semantic_instance.model = "gpt-oss:20b"
            mock_semantic_instance.get_health_status.return_value = ("healthy", "Ready")
            mock_semantic_instance.check_connection.return_value = True
            mock_semantic.return_value = mock_semantic_instance

            # Mock NL tag extractor
            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            # Mock NL search service
            mock_nl_service = MagicMock()
            mock_nl_service_class.return_value = mock_nl_service

            from src.api.schemas import ResourceItem
            from src.main import app

            # Default: return standard results with top-level reasoning
            mock_nl_service.search.return_value = (
                [
                    ResourceItem(
                        uuid="550e8400-e29b-41d4-a716-446655440001",
                        name="Hiking Basics",
                        summary="Starter guide for safe hiking in various terrains.",
                        link="/resources/550e8400-e29b-41d4-a716-446655440001",
                        tags=["hiking", "outdoor"],
                    ),
                    ResourceItem(
                        uuid="550e8400-e29b-41d4-a716-446655440002",
                        name="Trail Safety Guide",
                        summary="Essential safety tips for trail hiking.",
                        link="/resources/550e8400-e29b-41d4-a716-446655440002",
                        tags=["hiking", "safety"],
                    ),
                ],
                None,  # message
                [],  # candidate_tags
                "The query mentions 'hiking habits', which directly relates to the hiking and outdoor activity tags.",
            )

            with TestClient(app) as client:
                yield client

    def test_nl_search_response_has_required_fields(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify NLSearchResponse contains results, count, query, message, and candidate_tags."""
        response = client_with_mock_nl_search.get("/nl/search?q=show me hiking resources")

        assert response.status_code == 200
        data = response.json()

        # Check required fields per OpenAPI spec (T041)
        assert "results" in data
        assert "count" in data
        assert "query" in data
        assert "message" in data
        assert "candidate_tags" in data
        assert "reasoning" in data

    def test_nl_search_response_results_structure(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify each result has uuid, name, summary, link, tags; reasoning at top-level (T041)."""
        response = client_with_mock_nl_search.get("/nl/search?q=hiking tips")

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) > 0
        for result in data["results"]:
            # Required fields from FR-011
            assert "uuid" in result
            assert "name" in result
            assert "summary" in result
            assert "link" in result
            assert "tags" in result

            # Validate link format (T042)
            assert result["link"].startswith("/resources/")
            assert result["uuid"] in result["link"]

        # Validate top-level reasoning is present
        assert "reasoning" in data
        assert isinstance(data["reasoning"], str)

    def test_nl_search_response_count_matches_results(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify count field matches actual number of results (T041)."""
        response = client_with_mock_nl_search.get("/nl/search?q=outdoor activities")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == len(data["results"])

    def test_nl_search_response_echoes_query(self, client_with_mock_nl_search: TestClient) -> None:
        """Verify query field echoes the input query (T041)."""
        query = "show me resources that help me improve my hiking habits"
        response = client_with_mock_nl_search.get(f"/nl/search?q={query}")

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == query

    def test_nl_search_empty_results_structure(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify empty results still have correct structure (T027, US2)."""
        # Override mock for no-match scenario
        with patch.object(
            client_with_mock_nl_search.app.state.nl_search_service,
            "search",
            return_value=(
                [],
                "No matching resources found. Try searching with tags like: hiking, finance, health",
                ["hiking", "finance", "health"],
                "",
            ),
        ):
            response = client_with_mock_nl_search.get("/nl/search?q=xyzzy nonsense query")

            assert response.status_code == 200
            data = response.json()

            # Verify structure (T027)
            assert data["results"] == []
            assert data["count"] == 0
            assert data["message"] is not None
            assert len(data["candidate_tags"]) >= 2

    def test_nl_search_ambiguous_query_returns_candidate_tags(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify ambiguous queries return candidate tags and refinement message (T032, US3)."""
        # Override mock for ambiguity scenario
        with patch.object(
            client_with_mock_nl_search.app.state.nl_search_service,
            "search",
            return_value=(
                [],
                "Your query matches multiple categories. Did you mean: fitness, health? Please refine your query.",
                ["fitness", "health"],
                "Multiple tags match: fitness and health both relate to exercise.",
            ),
        ):
            response = client_with_mock_nl_search.get("/nl/search?q=exercise")

            assert response.status_code == 200
            data = response.json()

            # Verify ambiguity handling (T032)
            assert data["message"] is not None
            assert (
                "multiple categories" in data["message"].lower()
                or "refine" in data["message"].lower()
            )
            assert len(data["candidate_tags"]) >= 2
            assert data["count"] >= 0

    def test_nl_search_reasoning_field_not_empty_for_dspy_extraction(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify top-level reasoning contains DSPy explanation when available."""
        response = client_with_mock_nl_search.get("/nl/search?q=hiking resources")

        assert response.status_code == 200
        data = response.json()

        # Check that top-level reasoning is non-empty
        assert "reasoning" in data
        assert data["reasoning"] != ""
        assert len(data["reasoning"]) > 10  # Should be a meaningful explanation

    def test_nl_search_no_fabricated_links(self, client_with_mock_nl_search: TestClient) -> None:
        """Verify all links are internal deep links, no external/fabricated URLs (T042)."""
        response = client_with_mock_nl_search.get("/nl/search?q=hiking")

        assert response.status_code == 200
        data = response.json()

        for result in data["results"]:
            link = result["link"]
            # Must be internal deep link format
            assert link.startswith("/resources/")
            assert not link.startswith("http://")
            assert not link.startswith("https://")
            # UUID must be in the link
            assert result["uuid"] in link


class TestNLSearchErrorResponses:
    """Contract tests for error responses from /nl/search."""

    @pytest.fixture
    def client_with_mock_nl_search(self) -> Generator[TestClient]:
        """Create test client with mocked services."""
        with (
            patch("src.main.SemanticSearchService") as mock_semantic,
            patch("src.main.NLSearchService") as mock_nl_service_class,
            patch("src.main.NLTagExtractor") as mock_extractor_class,
        ):
            mock_semantic_instance = MagicMock()
            mock_semantic_instance.model = "gpt-oss:20b"
            mock_semantic_instance.get_health_status.return_value = ("healthy", "Ready")
            mock_semantic_instance.check_connection.return_value = True
            mock_semantic.return_value = mock_semantic_instance

            mock_extractor = MagicMock()
            mock_extractor_class.return_value = mock_extractor

            mock_nl_service = MagicMock()
            mock_nl_service_class.return_value = mock_nl_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_nl_search_missing_query_returns_400(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify missing query parameter returns 400 error."""
        response = client_with_mock_nl_search.get("/nl/search")

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        detail = data["detail"]
        assert "error" in detail
        assert "code" in detail
        assert detail["code"] == "MISSING_QUERY"

    def test_nl_search_empty_query_returns_400(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify empty query parameter returns 400 error."""
        response = client_with_mock_nl_search.get("/nl/search?q=")

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        detail = data["detail"]
        assert "error" in detail
        assert "code" in detail

    def test_nl_search_query_too_long_returns_400(
        self, client_with_mock_nl_search: TestClient
    ) -> None:
        """Verify query exceeding 1000 characters returns 400 error."""
        long_query = "a" * 1001
        response = client_with_mock_nl_search.get(f"/nl/search?q={long_query}")

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        detail = data["detail"]
        assert "error" in detail
        assert "code" in detail
        assert detail["code"] == "QUERY_TOO_LONG"
