"""Contract tests for /search endpoint response formats."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.models.resource import Resource


class TestSearchResponseFormat:
    """Contract tests verifying SearchResponse matches OpenAPI spec."""

    @pytest.fixture
    def client_with_mock_search(self) -> TestClient:
        """Create test client with mocked semantic search."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_matching.return_value = [
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
            mock_service.check_connection.return_value = True
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_search_response_has_required_fields(self, client_with_mock_search: TestClient) -> None:
        """Verify SearchResponse contains results, count, and query fields."""
        response = client_with_mock_search.get("/search?tag=home")

        assert response.status_code == 200
        data = response.json()

        # Check required fields per OpenAPI spec
        assert "results" in data
        assert "count" in data
        assert "query" in data

    def test_search_response_results_structure(self, client_with_mock_search: TestClient) -> None:
        """Verify each result has uuid, name, description, search_tag."""
        response = client_with_mock_search.get("/search?tag=home")

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) > 0
        for result in data["results"]:
            assert "uuid" in result
            assert "name" in result
            assert "description" in result
            assert "search_tag" in result

    def test_search_response_count_matches_results(
        self, client_with_mock_search: TestClient
    ) -> None:
        """Verify count field matches actual number of results."""
        response = client_with_mock_search.get("/search?tag=home")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == len(data["results"])

    def test_search_response_echoes_query(self, client_with_mock_search: TestClient) -> None:
        """Verify query field echoes the search tag."""
        response = client_with_mock_search.get("/search?tag=home")

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "home"

    def test_search_empty_results_structure(self, client_with_mock_search: TestClient) -> None:
        """Verify empty results still have correct structure."""
        # Override mock for this test
        with patch.object(
            client_with_mock_search.app.state.semantic_search,
            "find_matching",
            return_value=[],
        ):
            response = client_with_mock_search.get("/search?tag=xyzzy")

            assert response.status_code == 200
            data = response.json()

            assert data["results"] == []
            assert data["count"] == 0
            assert data["query"] == "xyzzy"


class TestSearchErrorResponseFormat:
    """Contract tests for search error responses."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.check_connection.return_value = True
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_missing_tag_error_format(self, client: TestClient) -> None:
        """Verify MISSING_TAG error has correct format."""
        response = client.get("/search")

        assert response.status_code == 400
        data = response.json()["detail"]

        assert data["error"] == "Tag parameter is required"
        assert data["code"] == "MISSING_TAG"
        assert "query" in data

    def test_empty_tag_error_format(self, client: TestClient) -> None:
        """Verify empty tag returns MISSING_TAG error."""
        response = client.get("/search?tag=")

        assert response.status_code == 400
        data = response.json()["detail"]

        assert data["code"] == "MISSING_TAG"

    def test_tag_too_long_error_format(self, client: TestClient) -> None:
        """Verify TAG_TOO_LONG error has correct format."""
        long_tag = "a" * 101
        response = client.get(f"/search?tag={long_tag}")

        assert response.status_code == 400
        data = response.json()["detail"]

        assert data["code"] == "TAG_TOO_LONG"
        assert "error" in data
        assert "query" in data

    def test_service_unavailable_error_format(self) -> None:
        """Verify SERVICE_UNAVAILABLE error has correct format."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_matching.side_effect = ConnectionError("unavailable")
            mock_service.check_connection.return_value = False
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                response = client.get("/search?tag=home")

                assert response.status_code == 503
                data = response.json()["detail"]

                assert data["code"] == "SERVICE_UNAVAILABLE"
                assert "error" in data
                assert data["query"] == "home"
