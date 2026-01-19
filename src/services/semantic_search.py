"""Semantic search service using DSPy with Ollama for tag matching."""

import logging
import subprocess
from typing import Literal

import dspy

from src.config import settings
from src.models.resource import Resource
from src.services.resource_store import ResourceStore

# Timeout constants for startup health checks (in seconds)
STARTUP_HTTP_TIMEOUT = 5.0
STARTUP_PS_TIMEOUT = 5.0

logger = logging.getLogger(__name__)


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
        self.ollama_host: str = ollama_host if ollama_host else settings.ollama_host
        self.model: str = model if model else settings.ollama_model

        # Initialize DSPy with Ollama
        self.lm = dspy.LM(
            f"ollama_chat/{self.model}",
            api_base=self.ollama_host,
            api_key="",
            cache=settings.dspy_cache_enabled,
        )
        dspy.configure(lm=self.lm)

        # Pre-build the available tags string for efficiency
        self._available_tags = ", ".join(resource_store.get_unique_tags())

        # Create the signature dynamically with actual tags in the description
        class SemanticResourceFinder(dspy.Signature):  # type: ignore[misc]
            """Classify a search tag to the best matching tag in the dataset.

            Given a search tag, identify the single tag from the dataset that is most
            semantically related. Consider synonyms, related concepts, and contextual
            similarity.
            """

            search_tag: str = dspy.InputField(
                desc="The tag to search for (e.g., 'home', 'car', 'technology')"
            )
            available_tags: str = dspy.InputField(
                desc=f"Available tags in the dataset: {self._available_tags}"
            )
            best_matching_tag: str = dspy.OutputField(
                desc=f"The single tag from this list that best matches the search tag: {self._available_tags}"
            )

        # Create the ChainOfThought module for semantic matching
        self.finder = dspy.ChainOfThought(SemanticResourceFinder)

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
            logger.info(f"Performing semantic search for tag: {search_tag}")
            result = self.finder(
                search_tag=search_tag,
                available_tags=self._available_tags,
            )

            # Extract the best matching tag from the result
            best_tag = result.best_matching_tag
            logger.info(f"Classified '{search_tag}' to tag: '{best_tag}'")

            # Handle case where result might need cleaning
            if isinstance(best_tag, str):
                best_tag = best_tag.strip()

            # Look up all resources with the classified tag
            resources = self.resource_store.get_by_tag(best_tag)
            logger.info(f"Retrieved {len(resources)} resources with tag '{best_tag}'")
            return resources

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
