"""Integration tests for the /resources (list all) API endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestListAPIIntegration:
    """Integration tests for the list all resources endpoint."""

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

    def test_list_returns_all_100_resources(self, client: TestClient) -> None:
        """Test that listing returns all 100 resources."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 100
        assert len(data["resources"]) == 100

    def test_list_resources_are_valid(self, client: TestClient) -> None:
        """Test that all listed resources have valid structure."""
        response = client.get("/resources")

        assert response.status_code == 200
        resources = response.json()["resources"]

        for resource in resources:
            # UUID should be valid format
            assert len(resource["uuid"]) == 36
            assert resource["uuid"].count("-") == 4

            # Other fields should be non-empty strings
            assert len(resource["name"]) > 0
            assert len(resource["description"]) > 0
            assert len(resource["search_tag"]) > 0

    def test_list_resources_have_unique_uuids(self, client: TestClient) -> None:
        """Test that all resources have unique UUIDs."""
        response = client.get("/resources")

        assert response.status_code == 200
        resources = response.json()["resources"]

        uuids = [r["uuid"] for r in resources]
        assert len(uuids) == len(set(uuids))

    def test_list_is_deterministic(self, client: TestClient) -> None:
        """Test that list returns same resources on repeated calls."""
        response1 = client.get("/resources")
        response2 = client.get("/resources")

        assert response1.status_code == 200
        assert response2.status_code == 200

        resources1 = response1.json()["resources"]
        resources2 = response2.json()["resources"]

        # Same order and content
        for r1, r2 in zip(resources1, resources2, strict=True):
            assert r1["uuid"] == r2["uuid"]
            assert r1["name"] == r2["name"]

    def test_list_resources_tags_are_from_categories(self, client: TestClient) -> None:
        """Test that all resource tags are from the expected categories."""
        from src.services.resource_store import TAG_CATEGORIES

        response = client.get("/resources")

        assert response.status_code == 200
        resources = response.json()["resources"]

        for resource in resources:
            assert resource["search_tag"] in TAG_CATEGORIES

    def test_list_response_is_json(self, client: TestClient) -> None:
        """Test that response content-type is JSON."""
        response = client.get("/resources")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_list_can_be_used_for_uuid_lookup(self, client: TestClient) -> None:
        """Test that UUIDs from list can be used for individual lookup."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]

        # Pick a few random resources and verify they can be looked up
        for i in [0, 49, 99]:  # First, middle, last
            uuid = resources[i]["uuid"]
            lookup_response = client.get(f"/resources/{uuid}")

            assert lookup_response.status_code == 200
            assert lookup_response.json()["resource"]["uuid"] == uuid
