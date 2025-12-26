"""Contract tests for /resources/{uuid} endpoint response formats."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestResourceResponseFormat:
    """Contract tests verifying ResourceResponse matches OpenAPI spec."""

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

    def test_resource_response_has_resource_wrapper(self, client: TestClient) -> None:
        """Verify ResourceResponse wraps resource in 'resource' field."""
        # First get a valid UUID from the list endpoint
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]

        response = client.get(f"/resources/{valid_uuid}")

        assert response.status_code == 200
        data = response.json()

        # Per OpenAPI spec, response should have 'resource' wrapper
        assert "resource" in data

    def test_resource_has_required_fields(self, client: TestClient) -> None:
        """Verify resource has uuid, name, description, search_tag."""
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

    def test_resource_uuid_matches_request(self, client: TestClient) -> None:
        """Verify returned resource has the requested UUID."""
        list_response = client.get("/resources")
        resources = list_response.json()["resources"]
        valid_uuid = resources[0]["uuid"]

        response = client.get(f"/resources/{valid_uuid}")

        assert response.status_code == 200
        resource = response.json()["resource"]

        assert resource["uuid"] == valid_uuid


class TestResourceErrorResponseFormat:
    """Contract tests for resource error responses."""

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

    def test_invalid_uuid_error_format(self, client: TestClient) -> None:
        """Verify INVALID_UUID error has correct format."""
        response = client.get("/resources/not-a-valid-uuid")

        assert response.status_code == 400
        data = response.json()["detail"]

        assert data["error"] == "Invalid UUID format"
        assert data["code"] == "INVALID_UUID"
        assert data["query"] == "not-a-valid-uuid"

    def test_resource_not_found_error_format(self, client: TestClient) -> None:
        """Verify RESOURCE_NOT_FOUND error has correct format."""
        # Valid UUID format but doesn't exist
        fake_uuid = "00000000-0000-4000-8000-000000000000"
        response = client.get(f"/resources/{fake_uuid}")

        assert response.status_code == 404
        data = response.json()["detail"]

        assert data["error"] == "Resource not found"
        assert data["code"] == "RESOURCE_NOT_FOUND"
        assert data["query"] == fake_uuid

    def test_malformed_uuid_variations(self, client: TestClient) -> None:
        """Test various malformed UUID formats return INVALID_UUID."""
        malformed_uuids = [
            "123",
            "not-uuid",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400_e29b_41d4_a716_446655440000",  # Wrong separator
        ]

        for bad_uuid in malformed_uuids:
            response = client.get(f"/resources/{bad_uuid}")
            assert response.status_code == 400, f"Expected 400 for {bad_uuid}"
            assert response.json()["detail"]["code"] == "INVALID_UUID"
