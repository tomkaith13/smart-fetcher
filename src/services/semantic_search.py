"""Semantic search service using DSPy with Ollama for tag matching."""

import json
import logging
import os
import subprocess
from typing import Literal

import dspy

from src.models.resource import Resource
from src.services.resource_store import ResourceStore

# Timeout constants for startup health checks (in seconds)
STARTUP_HTTP_TIMEOUT = 5.0
STARTUP_PS_TIMEOUT = 5.0

logger = logging.getLogger(__name__)


class SemanticResourceFinder(dspy.Signature):  # type: ignore[misc]
    """Find resources semantically related to a search tag.

    Given a search tag, identify all resources whose tags are semantically
    related to the search term. Consider synonyms, related concepts, and
    contextual similarity.
    """

    search_tag: str = dspy.InputField(
        desc="The tag to search for (e.g., 'home', 'car', 'technology')"
    )
    resources_context: str = dspy.InputField(
        desc="JSON list of all available resources with their tags"
    )
    matching_uuids: list[str] = dspy.OutputField(
        desc="UUIDs of resources whose tags are semantically related to the search tag"
    )


class SemanticSearchService:
    """Service for semantic tag-based resource search using DSPy and Ollama.

    Uses ChainOfThought reasoning to identify resources with semantically
    related tags, including synonyms and related concepts.
    """

    def __init__(
        self,
        resource_store: ResourceStore,
        ollama_host: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize the semantic search service.

        Args:
            resource_store: The resource store to search.
            ollama_host: Ollama API endpoint (default: http://localhost:11434).
            model: Model name to use (default: gpt-oss:20b).
        """
        self.resource_store = resource_store

        # Configuration from environment or defaults
        self.ollama_host: str = (
            ollama_host if ollama_host else os.getenv("OLLAMA_HOST") or "http://localhost:11434"
        )
        self.model: str = model if model else os.getenv("OLLAMA_MODEL") or "gpt-oss:20b"

        # Initialize DSPy with Ollama
        self.lm = dspy.LM(
            f"ollama_chat/{self.model}",
            api_base=self.ollama_host,
            api_key="",
        )
        dspy.configure(lm=self.lm)

        # Create the ChainOfThought module for semantic matching
        self.finder = dspy.ChainOfThought(SemanticResourceFinder)

        # Pre-build the context string for efficiency
        self._resources_context = json.dumps(resource_store.get_resources_context())

    def find_matching(self, search_tag: str) -> list[Resource]:
        """Find resources semantically related to the search tag.

        Args:
            search_tag: The tag to search for.

        Returns:
            List of matching Resource objects.

        Raises:
            ConnectionError: If Ollama service is unavailable or model not running.
        """
        # Early validation: check if model is available
        if not self.check_model_running():
            if not self.check_connection():
                raise ConnectionError(f"Ollama service is not reachable at {self.ollama_host}")
            raise ConnectionError(
                f"Model '{self.model}' is not running. Start it with: ollama run {self.model}"
            )

        try:
            result = self.finder(
                search_tag=search_tag,
                resources_context=self._resources_context,
            )

            # Extract matching UUIDs from the result
            matching_uuids = result.matching_uuids

            # Handle case where result might be a string representation
            if isinstance(matching_uuids, str):
                try:
                    matching_uuids = json.loads(matching_uuids)
                except json.JSONDecodeError:
                    matching_uuids = []

            # Ensure we have a list
            if not isinstance(matching_uuids, list):
                matching_uuids = []

            # Look up full resources by returned UUIDs
            return self.resource_store.get_by_uuids(matching_uuids)

        except Exception as e:
            # Check if it's a connection error
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
                raise ConnectionError(f"Ollama service unavailable: {e}") from e
            raise

    def check_model_running(self) -> bool:
        """Check if the configured model is running via ollama ps.

        Executes 'ollama ps' command to verify the model is loaded and ready
        to serve inference requests.

        Returns:
            True if the model is running, False otherwise.
        """
        try:
            # Run 'ollama ps' to list running models
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=STARTUP_PS_TIMEOUT,
                check=False,
            )

            # Check if command succeeded
            if result.returncode != 0:
                return False

            # Check if output is available
            if not result.stdout:
                return False

            # Parse output to see if our model is listed
            # Format: NAME        ID        SIZE    PROCESSOR    UNTIL
            output = result.stdout.lower()
            model_name = self.model.lower().split(":")[0]  # Extract base name

            # Check if model appears in the output
            return model_name in output

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning("ollama ps check failed: %s", str(e))
            return False

    def check_connection(self) -> bool:
        """Check if Ollama service is reachable.

        Returns:
            True if connected, False otherwise.
        """
        try:
            import httpx

            response = httpx.get(f"{self.ollama_host}/api/tags", timeout=STARTUP_HTTP_TIMEOUT)
            return response.status_code == 200
        except Exception:
            return False

    def get_health_status(self) -> tuple[Literal["healthy", "degraded", "unhealthy"], str]:
        """Get comprehensive health status of the semantic search service.

        Checks both Ollama connectivity and whether the required model is running.

        Returns:
            Tuple of (status, message) where status is 'healthy', 'degraded', or 'unhealthy'
            and message describes any issues.
        """
        # First check if Ollama service is reachable
        if not self.check_connection():
            return ("unhealthy", "Ollama service is not reachable")

        # Then check if the specific model is running
        if not self.check_model_running():
            return (
                "degraded",
                f"Ollama is running but model '{self.model}' is not loaded. "
                f"Run 'ollama run {self.model}' to start the model.",
            )

        return ("healthy", "Ollama and model are ready")
