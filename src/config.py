"""Application configuration loaded from environment variables and .env file.

This module provides centralized configuration management for the smart-fetcher
application, supporting both environment variables and .env file configuration.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file at module import time
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables and .env file.

    Attributes:
        ollama_host: Ollama API endpoint URL.
        ollama_model: Model name for semantic search and agent.
        nl_search_result_cap: Maximum results returned by NL search.
        agent_timeout_sec: Agent execution timeout in seconds.
        agent_max_tokens: Maximum tokens for agent response.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        dspy_cache_enabled: Enable DSPy LM response caching.
        dspy_cache_dir: Directory for DSPy cache storage.
    """

    # Ollama Configuration
    ollama_host: str
    ollama_model: str

    # Search Configuration
    nl_search_result_cap: int

    # Agent Configuration
    agent_timeout_sec: int
    agent_max_tokens: int

    # Logging
    log_level: str

    # DSPy Caching Configuration
    dspy_cache_enabled: bool
    dspy_cache_dir: str

    def configure_dspy_cache(self) -> None:
        """Set DSPY_CACHEDIR environment variable before LM initialization.

        Must be called before any dspy.LM initialization to take effect.
        DSPy reads the DSPY_CACHEDIR environment variable to determine where
        to store cached LM responses.
        """
        if self.dspy_cache_enabled:
            os.environ["DSPY_CACHEDIR"] = self.dspy_cache_dir


def _str_to_bool(value: str) -> bool:
    """Convert string to boolean (case-insensitive).

    Args:
        value: String value to convert ("true", "1", "yes", "on" are truthy).

    Returns:
        Boolean representation of the string value.
    """
    return value.lower() in ("true", "1", "yes", "on")


def load_settings() -> Settings:
    """Load settings from environment variables with defaults.

    Reads configuration from environment variables (or .env file loaded by
    python-dotenv) and returns a Settings instance with type-safe values.

    Returns:
        Settings instance with all configuration loaded.
    """
    return Settings(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gpt-oss:20b"),
        nl_search_result_cap=int(os.getenv("NL_SEARCH_RESULT_CAP", "5")),
        agent_timeout_sec=int(os.getenv("AGENT_TIMEOUT_SEC", "5")),
        agent_max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "1024")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        dspy_cache_enabled=_str_to_bool(os.getenv("DSPY_CACHE_ENABLED", "true")),
        dspy_cache_dir=os.getenv("DSPY_CACHE_DIR", "./.dspy_cache"),
    )


# Global settings instance
settings = load_settings()
