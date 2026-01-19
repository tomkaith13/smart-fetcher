"""Unit tests for configuration module."""

import os
from unittest.mock import patch

from src.config import Settings, _str_to_bool, load_settings


class TestStrToBool:
    """Tests for _str_to_bool helper function."""

    def test_true_values(self) -> None:
        """Test that various true-like strings are converted correctly."""
        assert _str_to_bool("true") is True
        assert _str_to_bool("TRUE") is True
        assert _str_to_bool("True") is True
        assert _str_to_bool("1") is True
        assert _str_to_bool("yes") is True
        assert _str_to_bool("YES") is True
        assert _str_to_bool("on") is True
        assert _str_to_bool("ON") is True

    def test_false_values(self) -> None:
        """Test that non-true strings are converted to False."""
        assert _str_to_bool("false") is False
        assert _str_to_bool("FALSE") is False
        assert _str_to_bool("0") is False
        assert _str_to_bool("no") is False
        assert _str_to_bool("off") is False
        assert _str_to_bool("") is False
        assert _str_to_bool("random") is False


class TestLoadSettings:
    """Tests for load_settings function."""

    def test_load_settings_defaults(self) -> None:
        """Test that load_settings returns correct defaults."""
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
            assert settings.ollama_host == "http://localhost:11434"
            assert settings.ollama_model == "gpt-oss:20b"
            assert settings.nl_search_result_cap == 5
            assert settings.agent_timeout_sec == 5
            assert settings.agent_max_tokens == 1024
            assert settings.log_level == "INFO"
            assert settings.dspy_cache_enabled is True
            assert settings.dspy_cache_dir == "./.dspy_cache"

    def test_load_settings_from_env(self) -> None:
        """Test that load_settings reads from environment variables."""
        env_vars = {
            "OLLAMA_HOST": "http://custom-host:9999",
            "OLLAMA_MODEL": "custom-model",
            "NL_SEARCH_RESULT_CAP": "10",
            "AGENT_TIMEOUT_SEC": "15",
            "AGENT_MAX_TOKENS": "2048",
            "LOG_LEVEL": "DEBUG",
            "DSPY_CACHE_ENABLED": "false",
            "DSPY_CACHE_DIR": "/custom/cache/dir",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = load_settings()
            assert settings.ollama_host == "http://custom-host:9999"
            assert settings.ollama_model == "custom-model"
            assert settings.nl_search_result_cap == 10
            assert settings.agent_timeout_sec == 15
            assert settings.agent_max_tokens == 2048
            assert settings.log_level == "DEBUG"
            assert settings.dspy_cache_enabled is False
            assert settings.dspy_cache_dir == "/custom/cache/dir"

    def test_type_coercion_int(self) -> None:
        """Test that string integers are correctly coerced to int."""
        with patch.dict(
            os.environ, {"NL_SEARCH_RESULT_CAP": "7", "AGENT_TIMEOUT_SEC": "20"}, clear=True
        ):
            settings = load_settings()
            assert isinstance(settings.nl_search_result_cap, int)
            assert settings.nl_search_result_cap == 7
            assert isinstance(settings.agent_timeout_sec, int)
            assert settings.agent_timeout_sec == 20

    def test_type_coercion_bool(self) -> None:
        """Test that string booleans are correctly coerced to bool."""
        with patch.dict(os.environ, {"DSPY_CACHE_ENABLED": "1"}, clear=True):
            settings = load_settings()
            assert isinstance(settings.dspy_cache_enabled, bool)
            assert settings.dspy_cache_enabled is True

        with patch.dict(os.environ, {"DSPY_CACHE_ENABLED": "false"}, clear=True):
            settings = load_settings()
            assert isinstance(settings.dspy_cache_enabled, bool)
            assert settings.dspy_cache_enabled is False


class TestSettings:
    """Tests for Settings dataclass."""

    def test_configure_dspy_cache_enabled(self) -> None:
        """Test that configure_dspy_cache sets DSPY_CACHEDIR when enabled."""
        settings = Settings(
            ollama_host="http://localhost:11434",
            ollama_model="gpt-oss:20b",
            nl_search_result_cap=5,
            agent_timeout_sec=5,
            agent_max_tokens=1024,
            log_level="INFO",
            dspy_cache_enabled=True,
            dspy_cache_dir="/test/cache/dir",
        )

        # Clear any existing DSPY_CACHEDIR
        if "DSPY_CACHEDIR" in os.environ:
            del os.environ["DSPY_CACHEDIR"]

        settings.configure_dspy_cache()
        assert os.environ["DSPY_CACHEDIR"] == "/test/cache/dir"

    def test_configure_dspy_cache_disabled(self) -> None:
        """Test that configure_dspy_cache does not set DSPY_CACHEDIR when disabled."""
        settings = Settings(
            ollama_host="http://localhost:11434",
            ollama_model="gpt-oss:20b",
            nl_search_result_cap=5,
            agent_timeout_sec=5,
            agent_max_tokens=1024,
            log_level="INFO",
            dspy_cache_enabled=False,
            dspy_cache_dir="/test/cache/dir",
        )

        # Clear any existing DSPY_CACHEDIR
        if "DSPY_CACHEDIR" in os.environ:
            del os.environ["DSPY_CACHEDIR"]

        settings.configure_dspy_cache()
        assert "DSPY_CACHEDIR" not in os.environ

    def test_settings_dataclass_fields(self) -> None:
        """Test that Settings dataclass has all required fields."""
        settings = Settings(
            ollama_host="http://test:11434",
            ollama_model="test-model",
            nl_search_result_cap=3,
            agent_timeout_sec=10,
            agent_max_tokens=512,
            log_level="WARNING",
            dspy_cache_enabled=False,
            dspy_cache_dir="/cache",
        )

        assert settings.ollama_host == "http://test:11434"
        assert settings.ollama_model == "test-model"
        assert settings.nl_search_result_cap == 3
        assert settings.agent_timeout_sec == 10
        assert settings.agent_max_tokens == 512
        assert settings.log_level == "WARNING"
        assert settings.dspy_cache_enabled is False
        assert settings.dspy_cache_dir == "/cache"
