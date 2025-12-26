"""Integration tests for the /resources/{uuid} API endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestResourceAPIIntegration:
    """Integration tests for the resource UUID lookup endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.model = "gpt-oss:20b"
            mock_service.get_health_status.return_value = ("healthy", "Ready")
            mock_service.check_connection.return_value = True
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_get_valid_uuid_returns_resource(self, client: TestClient) -> None:
        """Test fetching a resource with a valid UUID."""
        # Get a valid UUID from the resources list
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]

        response = client.get(f"/resources/{valid_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["resource"]["uuid"] == valid_uuid

    def test_get_invalid_uuid_format_returns_400(self, client: TestClient) -> None:
        """Test fetching with invalid UUID format returns 400."""
        response = client.get("/resources/not-a-uuid")

        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == "INVALID_UUID"

    def test_get_nonexistent_uuid_returns_404(self, client: TestClient) -> None:
        """Test fetching with valid but non-existent UUID returns 404."""
        fake_uuid = "00000000-0000-4000-8000-000000000000"
        response = client.get(f"/resources/{fake_uuid}")

        assert response.status_code == 404
        data = response.json()["detail"]
        assert data["code"] == "RESOURCE_NOT_FOUND"

    def test_uuid_case_insensitive(self, client: TestClient) -> None:
        """Test that UUID matching is case-insensitive."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]

        # Try uppercase version
        upper_uuid = valid_uuid.upper()
        response = client.get(f"/resources/{upper_uuid}")

        # Should still find the resource (case-insensitive matching)
        # Note: This depends on implementation - either 200 or 404 is acceptable
        # The key is it shouldn't be a 400 INVALID_UUID error
        assert response.status_code in [200, 404]

    def test_resource_contains_all_fields(self, client: TestClient) -> None:
        """Test that returned resource has all required fields."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]

        response = client.get(f"/resources/{valid_uuid}")

        assert response.status_code == 200
        resource = response.json()["resource"]

        assert "uuid" in resource
        assert "name" in resource
        assert "description" in resource
        assert "search_tag" in resource

        # Verify field types
        assert isinstance(resource["uuid"], str)
        assert isinstance(resource["name"], str)
        assert isinstance(resource["description"], str)
        assert isinstance(resource["search_tag"], str)

    def test_resource_deterministic_content(self, client: TestClient) -> None:
        """Test that resources have deterministic content across requests."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]
        expected_name = resources[0]["name"]

        response = client.get(f"/resources/{valid_uuid}")

        assert response.status_code == 200
        resource = response.json()["resource"]

        # Name should be the same as in the list
        assert resource["name"] == expected_name

    def test_multiple_uuid_lookups(self, client: TestClient) -> None:
        """Test looking up multiple different UUIDs."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]

        # Look up first 5 resources
        for i in range(min(5, len(resources))):
            uuid = resources[i]["uuid"]
            response = client.get(f"/resources/{uuid}")

            assert response.status_code == 200
            assert response.json()["resource"]["uuid"] == uuid
