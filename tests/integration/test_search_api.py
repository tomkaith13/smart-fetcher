"""Integration tests for the /search API endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.models.resource import Resource


class TestSearchAPIIntegration:
    """Integration tests for the search endpoint."""

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

    def test_search_valid_tag_returns_results(self, client_with_mock_search: TestClient) -> None:
        """Test searching with a valid tag returns matching resources."""
        response = client_with_mock_search.get("/search?tag=home")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 2
        assert len(data["results"]) == 2
        assert data["query"] == "home"

    def test_search_empty_tag_returns_400(self, client_with_mock_search: TestClient) -> None:
        """Test searching with empty tag returns 400 error."""
        response = client_with_mock_search.get("/search?tag=")

        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == "MISSING_TAG"

    def test_search_missing_tag_returns_400(self, client_with_mock_search: TestClient) -> None:
        """Test searching without tag parameter returns 400 error."""
        response = client_with_mock_search.get("/search")

        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == "MISSING_TAG"

    def test_search_whitespace_tag_returns_400(self, client_with_mock_search: TestClient) -> None:
        """Test searching with whitespace-only tag returns 400 error."""
        response = client_with_mock_search.get("/search?tag=   ")

        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == "MISSING_TAG"

    def test_search_tag_too_long_returns_400(self, client_with_mock_search: TestClient) -> None:
        """Test searching with tag >100 chars returns 400 error."""
        long_tag = "a" * 101
        response = client_with_mock_search.get(f"/search?tag={long_tag}")

        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == "TAG_TOO_LONG"

    def test_search_tag_exactly_100_chars_succeeds(
        self, client_with_mock_search: TestClient
    ) -> None:
        """Test searching with exactly 100 char tag succeeds."""
        tag_100 = "a" * 100
        response = client_with_mock_search.get(f"/search?tag={tag_100}")

        # Should succeed (200) or return empty results, not an error
        assert response.status_code == 200

    def test_search_no_matches_returns_empty_list(self) -> None:
        """Test searching with no matches returns empty results."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_matching.return_value = []
            mock_service.check_connection.return_value = True
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                response = client.get("/search?tag=xyzzy")

                assert response.status_code == 200
                data = response.json()
                assert data["count"] == 0
                assert data["results"] == []
                assert data["query"] == "xyzzy"

    def test_search_service_unavailable_returns_503(self) -> None:
        """Test that service unavailability returns 503 error."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_matching.side_effect = ConnectionError("Ollama service unavailable")
            mock_service.check_connection.return_value = False
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                response = client.get("/search?tag=home")

                assert response.status_code == 503
                data = response.json()["detail"]
                assert data["code"] == "SERVICE_UNAVAILABLE"

    def test_search_trims_whitespace_from_tag(self, client_with_mock_search: TestClient) -> None:
        """Test that whitespace around tag is trimmed."""
        response = client_with_mock_search.get("/search?tag=  home  ")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "home"

    def test_search_preserves_case(self, client_with_mock_search: TestClient) -> None:
        """Test that tag case is preserved in query echo."""
        response = client_with_mock_search.get("/search?tag=Home")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Home"

    def test_search_with_special_characters(self, client_with_mock_search: TestClient) -> None:
        """Test searching with special characters in tag."""
        response = client_with_mock_search.get("/search?tag=home-office")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "home-office"
