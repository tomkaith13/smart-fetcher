"""Contract tests for /health endpoint response formats."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthResponseFormat:
    """Contract tests verifying HealthResponse matches expected schema."""

    @pytest.fixture
    def client_with_mock_service(self) -> TestClient:
        """Create test client with mocked semantic search service."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = (
                "healthy",
                "Ollama and model are ready",
            )
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_health_response_has_required_fields(
        self, client_with_mock_service: TestClient
    ) -> None:
        """Verify HealthResponse contains all required fields."""
        response = client_with_mock_service.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "status" in data, "status field is required"
        assert "ollama" in data, "ollama field is required"
        assert "ollama_message" in data, "ollama_message field is required"
        assert "resources_loaded" in data, "resources_loaded field is required"

    def test_health_response_field_types(self, client_with_mock_service: TestClient) -> None:
        """Verify HealthResponse fields have correct types."""
        response = client_with_mock_service.get("/health")
        data = response.json()

        assert isinstance(data["status"], str), "status must be a string"
        assert isinstance(data["ollama"], str), "ollama must be a string"
        assert isinstance(data["ollama_message"], str), "ollama_message must be a string"
        assert isinstance(data["resources_loaded"], int), "resources_loaded must be an integer"

    def test_health_response_status_values(self, client_with_mock_service: TestClient) -> None:
        """Verify status field contains valid values."""
        response = client_with_mock_service.get("/health")
        data = response.json()

        valid_statuses = ["healthy", "degraded", "unhealthy"]
        assert data["status"] in valid_statuses, (
            f"status must be one of {valid_statuses}, got {data['status']}"
        )

    def test_health_response_ollama_values(self, client_with_mock_service: TestClient) -> None:
        """Verify ollama field contains valid values."""
        response = client_with_mock_service.get("/health")
        data = response.json()

        valid_ollama_statuses = ["connected", "model_not_running", "disconnected", "unknown"]
        assert data["ollama"] in valid_ollama_statuses, (
            f"ollama must be one of {valid_ollama_statuses}, got {data['ollama']}"
        )

    def test_health_response_resources_loaded_non_negative(
        self, client_with_mock_service: TestClient
    ) -> None:
        """Verify resources_loaded is non-negative."""
        response = client_with_mock_service.get("/health")
        data = response.json()

        assert data["resources_loaded"] >= 0, "resources_loaded must be non-negative"

    def test_health_response_degraded_structure(self) -> None:
        """Verify response structure when service is degraded."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = (
                "degraded",
                "Model not loaded",
            )
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                response = client.get("/health")

                assert response.status_code == 200
                data = response.json()

                assert data["status"] == "degraded"
                assert data["ollama"] == "model_not_running"
                assert len(data["ollama_message"]) > 0

    def test_health_response_unhealthy_structure(self) -> None:
        """Verify response structure when service is unhealthy."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = (
                "unhealthy",
                "Service not reachable",
            )
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                response = client.get("/health")

                assert response.status_code == 200
                data = response.json()

                assert data["status"] == "unhealthy"
                assert data["ollama"] == "disconnected"
                assert len(data["ollama_message"]) > 0

    def test_health_response_message_not_empty(self, client_with_mock_service: TestClient) -> None:
        """Verify ollama_message provides actionable information."""
        response = client_with_mock_service.get("/health")
        data = response.json()

        # Message should provide useful information
        assert len(data["ollama_message"]) > 0, "ollama_message should not be empty"
        assert isinstance(data["ollama_message"], str), "ollama_message must be a string"
