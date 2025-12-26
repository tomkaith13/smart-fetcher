"""Unit tests for SemanticSearchService."""

from unittest.mock import MagicMock, patch

import pytest

from src.models.resource import Resource
from src.services.resource_store import ResourceStore
from src.services.semantic_search import SemanticSearchService


class TestSemanticSearchService:
    """Tests for the SemanticSearchService class."""

    @pytest.fixture
    def mock_resource_store(self, sample_resources: list[Resource]) -> ResourceStore:
        """Create a resource store with sample data."""
        return ResourceStore(resources=sample_resources)

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_find_matching_returns_resources(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching returns matching resources."""
        # Mock model running
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gpt-oss:20b    abc123    10GB    100%\n"
        mock_subprocess.return_value = mock_result

        # Setup mock to return a matching tag
        mock_finder = MagicMock()
        mock_result = MagicMock()
        mock_result.best_matching_tag = "home"
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("house")

        # Should return all resources with the 'home' tag
        assert len(results) > 0
        assert all(isinstance(r, Resource) for r in results)
        assert all(r.search_tag == "home" for r in results)

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_find_matching_empty_results(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching handles no matches gracefully."""
        # Mock model running
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gpt-oss:20b    abc123    10GB    100%\n"
        mock_subprocess.return_value = mock_result

        mock_finder = MagicMock()
        mock_result = MagicMock()
        mock_result.best_matching_tag = "nonexistent"
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("xyzzy")

        assert results == []

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_find_matching_handles_string_with_whitespace(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching handles tag strings with whitespace."""
        # Mock model running
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gpt-oss:20b    abc123    10GB    100%\n"
        mock_subprocess.return_value = mock_result

        mock_finder = MagicMock()
        mock_result = MagicMock()
        # LLM might return a tag with whitespace
        mock_result.best_matching_tag = "  home  "
        mock_finder.return_value = mock_result
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)
        results = service.find_matching("house")

        # Should still find resources with 'home' tag after stripping
        assert len(results) > 0
        assert all(r.search_tag == "home" for r in results)

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_find_matching_connection_error(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test that find_matching raises ConnectionError when Ollama unavailable."""
        mock_finder = MagicMock()
        mock_finder.side_effect = Exception("Connection refused")
        mock_cot.return_value = mock_finder

        service = SemanticSearchService(resource_store=mock_resource_store)

        with pytest.raises(ConnectionError):
            service.find_matching("home")

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    def test_check_connection_success(
        self,
        mock_get: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_connection returns True when Ollama is reachable."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_connection() is True

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    def test_check_connection_failure(
        self,
        mock_get: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_connection returns False when Ollama is unreachable."""
        mock_get.side_effect = Exception("Connection refused")

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_connection() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    def test_service_uses_environment_config(
        self,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that service reads configuration from environment variables."""
        monkeypatch.setenv("OLLAMA_HOST", "http://custom-host:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

        service = SemanticSearchService(resource_store=mock_resource_store)

        assert service.ollama_host == "http://custom-host:11434"
        assert service.model == "custom-model"

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_check_model_running_success(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_model_running returns True when model is listed in ollama ps."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "NAME           ID        SIZE    PROCESSOR\ngpt-oss:20b    abc123    10GB    100%\n"
        )
        mock_subprocess.return_value = mock_result

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_model_running() is True

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_check_model_running_model_not_found(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_model_running returns False when model is not in output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "NAME           ID        SIZE    PROCESSOR\nother-model    xyz789    5GB     50%\n"
        )
        mock_subprocess.return_value = mock_result

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_model_running() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_check_model_running_command_fails(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_model_running returns False when subprocess fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_model_running() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_check_model_running_timeout(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_model_running returns False on timeout."""
        import subprocess

        mock_subprocess.side_effect = subprocess.TimeoutExpired("ollama", 5.0)

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_model_running() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_check_model_running_ollama_not_installed(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test check_model_running returns False when ollama CLI not found."""
        mock_subprocess.side_effect = FileNotFoundError()

        service = SemanticSearchService(resource_store=mock_resource_store)
        assert service.check_model_running() is False

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    @patch("subprocess.run")
    def test_get_health_status_healthy(
        self,
        mock_subprocess: MagicMock,
        mock_httpx: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test get_health_status returns healthy when both checks pass."""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_httpx.return_value = mock_response

        # Mock model running
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "gpt-oss:20b    abc123    10GB    100%\n"
        mock_subprocess.return_value = mock_result

        service = SemanticSearchService(resource_store=mock_resource_store)
        status, message = service.get_health_status()

        assert status == "healthy"
        assert "ready" in message.lower()

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    @patch("subprocess.run")
    def test_get_health_status_degraded_model_not_running(
        self,
        mock_subprocess: MagicMock,
        mock_httpx: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test get_health_status returns degraded when model not running."""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_httpx.return_value = mock_response

        # Mock model NOT running
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "other-model    xyz789    5GB    50%\n"
        mock_subprocess.return_value = mock_result

        service = SemanticSearchService(resource_store=mock_resource_store)
        status, message = service.get_health_status()

        assert status == "degraded"
        assert "not loaded" in message
        assert "ollama run" in message

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("httpx.get")
    def test_get_health_status_unhealthy_service_down(
        self,
        mock_httpx: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test get_health_status returns unhealthy when Ollama unreachable."""
        mock_httpx.side_effect = Exception("Connection refused")

        service = SemanticSearchService(resource_store=mock_resource_store)
        status, message = service.get_health_status()

        assert status == "unhealthy"
        assert "not reachable" in message

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_find_matching_fails_early_when_model_not_running(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test find_matching raises ConnectionError early when model not running."""
        # Mock httpx for connection check
        with patch("httpx.get") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_httpx.return_value = mock_response

            # Mock model NOT running
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_subprocess.return_value = mock_result

            service = SemanticSearchService(resource_store=mock_resource_store)

            with pytest.raises(ConnectionError) as exc_info:
                service.find_matching("home")

            assert "not running" in str(exc_info.value)
            assert "ollama run" in str(exc_info.value)

    @patch("src.services.semantic_search.dspy.LM")
    @patch("src.services.semantic_search.dspy.configure")
    @patch("src.services.semantic_search.dspy.ChainOfThought")
    @patch("subprocess.run")
    def test_find_matching_fails_early_when_service_down(
        self,
        mock_subprocess: MagicMock,
        mock_cot: MagicMock,
        mock_configure: MagicMock,
        mock_lm: MagicMock,
        mock_resource_store: ResourceStore,
    ) -> None:
        """Test find_matching raises ConnectionError when Ollama service down."""
        # Mock httpx for connection check to fail
        with patch("httpx.get") as mock_httpx:
            mock_httpx.side_effect = Exception("Connection refused")

            # Mock model check (won't be reached but setup anyway)
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_subprocess.return_value = mock_result

            service = SemanticSearchService(resource_store=mock_resource_store)

            with pytest.raises(ConnectionError) as exc_info:
                service.find_matching("home")

            assert "not reachable" in str(exc_info.value)
