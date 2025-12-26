"""Contract tests for /resources endpoint response formats."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestListResponseFormat:
    """Contract tests verifying ListResponse matches OpenAPI spec."""

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

    def test_list_response_has_required_fields(self, client: TestClient) -> None:
        """Verify ListResponse contains resources and count fields."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        # Check required fields per OpenAPI spec
        assert "resources" in data
        assert "count" in data

    def test_list_response_resources_is_array(self, client: TestClient) -> None:
        """Verify resources field is an array."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["resources"], list)

    def test_list_response_count_is_integer(self, client: TestClient) -> None:
        """Verify count field is an integer."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["count"], int)

    def test_list_response_count_matches_resources(self, client: TestClient) -> None:
        """Verify count matches number of resources."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == len(data["resources"])

    def test_each_resource_has_required_fields(self, client: TestClient) -> None:
        """Verify each resource has uuid, name, description, search_tag."""
        response = client.get("/resources")

        assert response.status_code == 200
        resources = response.json()["resources"]

        for resource in resources:
            assert "uuid" in resource
            assert "name" in resource
            assert "description" in resource
            assert "search_tag" in resource

    def test_resource_field_types(self, client: TestClient) -> None:
        """Verify resource fields have correct types."""
        response = client.get("/resources")

        assert response.status_code == 200
        resources = response.json()["resources"]

        for resource in resources:
            assert isinstance(resource["uuid"], str)
            assert isinstance(resource["name"], str)
            assert isinstance(resource["description"], str)
            assert isinstance(resource["search_tag"], str)

    def test_list_returns_500_resources(self, client: TestClient) -> None:
        """Verify exactly 500 resources are returned."""
        response = client.get("/resources")

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 500
        assert len(data["resources"]) == 500
