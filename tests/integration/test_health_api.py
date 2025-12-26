"""Integration tests for the /health API endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthAPIIntegration:
    """Integration tests for the health check endpoint."""

    @pytest.fixture
    def client_with_healthy_service(self) -> TestClient:
        """Create test client with healthy semantic search service."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = ("healthy", "Ollama and model are ready")
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    @pytest.fixture
    def client_with_degraded_service(self) -> TestClient:
        """Create test client with degraded semantic search (model not running)."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = (
                "degraded",
                "Ollama is running but model 'gpt-oss:20b' is not loaded. "
                "Run 'ollama run gpt-oss:20b' to start the model.",
            )
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    @pytest.fixture
    def client_with_unhealthy_service(self) -> TestClient:
        """Create test client with unhealthy semantic search (service down)."""
        with patch("src.main.SemanticSearchService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_health_status.return_value = (
                "unhealthy",
                "Ollama service is not reachable",
            )
            mock_service_class.return_value = mock_service

            from src.main import app

            with TestClient(app) as client:
                yield client

    def test_health_check_healthy(self, client_with_healthy_service: TestClient) -> None:
        """Test health endpoint returns healthy when all checks pass."""
        response = client_with_healthy_service.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["ollama"] == "connected"
        assert "ready" in data["ollama_message"].lower()
        assert data["resources_loaded"] == 100

    def test_health_check_degraded_model_not_running(
        self, client_with_degraded_service: TestClient
    ) -> None:
        """Test health endpoint returns degraded when model not running."""
        response = client_with_degraded_service.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "degraded"
        assert data["ollama"] == "model_not_running"
        assert "not loaded" in data["ollama_message"]
        assert "ollama run" in data["ollama_message"]
        assert data["resources_loaded"] == 100

    def test_health_check_unhealthy_service_down(
        self, client_with_unhealthy_service: TestClient
    ) -> None:
        """Test health endpoint returns unhealthy when Ollama unreachable."""
        response = client_with_unhealthy_service.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["ollama"] == "disconnected"
        assert "not reachable" in data["ollama_message"]
        assert data["resources_loaded"] == 100

    def test_health_check_response_structure(self, client_with_healthy_service: TestClient) -> None:
        """Test health endpoint returns correct response structure."""
        response = client_with_healthy_service.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "status" in data
        assert "ollama" in data
        assert "ollama_message" in data
        assert "resources_loaded" in data

        # Verify types
        assert isinstance(data["status"], str)
        assert isinstance(data["ollama"], str)
        assert isinstance(data["ollama_message"], str)
        assert isinstance(data["resources_loaded"], int)
