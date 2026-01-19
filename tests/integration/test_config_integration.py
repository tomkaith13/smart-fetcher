"""Integration tests for configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestConfigIntegration:
    """Integration tests for config loading and DSPy cache setup."""

    def test_env_file_loading(self) -> None:
        """Test that .env file is loaded correctly via python-dotenv."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp_env:
            tmp_env.write("OLLAMA_HOST=http://test-host:9999\n")
            tmp_env.write("DSPY_CACHE_ENABLED=false\n")
            tmp_env.write("DSPY_CACHE_DIR=/tmp/test_cache\n")
            tmp_env_path = tmp_env.name

        try:
            # Clear any existing environment variables
            with patch.dict(os.environ, {}, clear=True):
                # Load the .env file
                from dotenv import load_dotenv

                load_dotenv(tmp_env_path)

                # Import and load settings
                from src.config import load_settings

                settings = load_settings()

                # Verify values from .env file were loaded
                assert settings.ollama_host == "http://test-host:9999"
                assert settings.dspy_cache_enabled is False
                assert settings.dspy_cache_dir == "/tmp/test_cache"
        finally:
            # Clean up temp file
            Path(tmp_env_path).unlink()

    def test_configure_dspy_cache_sets_env_var(self) -> None:
        """Test that configure_dspy_cache sets DSPY_CACHEDIR environment variable."""
        from src.config import Settings

        # Create settings with cache enabled
        settings = Settings(
            ollama_host="http://localhost:11434",
            ollama_model="gpt-oss:20b",
            nl_search_result_cap=5,
            agent_timeout_sec=5,
            agent_max_tokens=1024,
            log_level="INFO",
            dspy_cache_enabled=True,
            dspy_cache_dir="/integration/test/cache",
        )

        # Clear DSPY_CACHEDIR if it exists
        if "DSPY_CACHEDIR" in os.environ:
            del os.environ["DSPY_CACHEDIR"]

        # Configure cache
        settings.configure_dspy_cache()

        # Verify DSPY_CACHEDIR was set
        assert os.environ["DSPY_CACHEDIR"] == "/integration/test/cache"

    def test_env_override_precedence(self) -> None:
        """Test that environment variables override .env file values."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp_env:
            tmp_env.write("OLLAMA_MODEL=dotenv-model\n")
            tmp_env.write("DSPY_CACHE_ENABLED=true\n")
            tmp_env_path = tmp_env.name

        try:
            # Set environment variable that should override .env
            with patch.dict(
                os.environ, {"OLLAMA_MODEL": "env-override-model", "DSPY_CACHE_ENABLED": "false"}
            ):
                # Load the .env file
                from dotenv import load_dotenv

                load_dotenv(tmp_env_path)

                # Import and load settings
                from src.config import load_settings

                settings = load_settings()

                # Environment variable should take precedence
                assert settings.ollama_model == "env-override-model"
                assert settings.dspy_cache_enabled is False
        finally:
            # Clean up temp file
            Path(tmp_env_path).unlink()

    def test_configure_dspy_cache_when_disabled(self) -> None:
        """Test that configure_dspy_cache does not set env var when disabled."""
        from src.config import Settings

        # Create settings with cache disabled
        settings = Settings(
            ollama_host="http://localhost:11434",
            ollama_model="gpt-oss:20b",
            nl_search_result_cap=5,
            agent_timeout_sec=5,
            agent_max_tokens=1024,
            log_level="INFO",
            dspy_cache_enabled=False,
            dspy_cache_dir="/should/not/be/set",
        )

        # Clear DSPY_CACHEDIR if it exists
        if "DSPY_CACHEDIR" in os.environ:
            del os.environ["DSPY_CACHEDIR"]

        # Configure cache
        settings.configure_dspy_cache()

        # Verify DSPY_CACHEDIR was NOT set
        assert "DSPY_CACHEDIR" not in os.environ
