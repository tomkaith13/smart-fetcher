"""ReACT-style agent using DSPy with NL search and resource validation tools."""

import logging
import os
import uuid
from typing import Any

import dspy

from src.api.schemas import AGENT_TIMEOUT_SEC, AgentErrorCode, ResourceCitation
from src.services.nl_search_service import NLSearchService
from src.utils.agent_logger import get_agent_logger
from src.utils.link_verifier import LinkVerifier

# Get a standard Python logger for hallucination detection
hallucination_logger = logging.getLogger(__name__)


class QASignature(dspy.Signature):  # type: ignore[misc]
    """Signature for question answering."""

    question: str = dspy.InputField(desc="User's natural language question")
    answer: str = dspy.OutputField(desc="Comprehensive answer to the question")


class ReACTAgent:
    """ReACT-style agent that uses NL search and resource validation tools.

    This agent orchestrates tool calls to answer user queries. It:
    1. Searches for relevant resources using NL search
    2. Validates resource URLs if needed
    3. Generates a final answer with optional resource citations
    """

    def __init__(
        self,
        nl_search_service: NLSearchService,
        link_verifier: LinkVerifier,
        model_name: str | None = None,
    ) -> None:
        """Initialize the ReACT agent.

        Args:
            nl_search_service: Service for natural language search.
            link_verifier: Service for validating resource URLs.
            model_name: DSPy model name (defaults to OLLAMA_MODEL env var).
        """
        self.nl_search_service = nl_search_service
        self.link_verifier = link_verifier
        self.logger = get_agent_logger()
        self.timeout_sec = AGENT_TIMEOUT_SEC
        self.current_session_id: str | None = None

        # Initialize DSPy with Ollama
        model_name = model_name or os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

        try:
            self.lm = dspy.LM(f"ollama/{model_name}", api_base=ollama_host)
            dspy.configure(lm=self.lm)
        except Exception as e:
            # Graceful fallback if Ollama unavailable
            self.lm = None
            self.logger.log_tool_action(
                agent_session_id="system",
                tool="dspy_init",
                params={"model": model_name, "host": ollama_host},
                result_summary=f"Failed to initialize DSPy: {e}",
            )
            self.react_agent = None
            return

        # Define tools for ReAct agent
        self.tools = [
            dspy.Tool(
                func=self._nl_search_tool,
                name="search_resources",
                desc="Search for resources using natural language query. Returns list of relevant resources with titles, summaries, and links.",
                args={"query": "Natural language search query"},
            ),
            dspy.Tool(
                func=self._validate_resource_tool,
                name="validate_resource",
                desc="Validate if a resource link is valid and accessible. Returns validation status.",
                args={"url": "Resource URL or internal link to validate"},
            ),
        ]

        # Create ReAct agent with tools
        try:
            self.react_agent = dspy.ReAct(QASignature, tools=self.tools, max_iters=5)
        except Exception as e:
            self.logger.log_tool_action(
                agent_session_id="system",
                tool="react_init",
                params={"signature": "QASignature", "tools": len(self.tools)},
                result_summary=f"Failed to initialize ReAct: {e}",
            )
            self.react_agent = None

    def _nl_search_tool(self, query: str) -> str:
        """Tool function for NL search (called by DSPy ReAct).

        Args:
            query: Natural language search query.

        Returns:
            String representation of search results.
        """
        session_id = self.current_session_id or "unknown"
        try:
            resource_items, message, candidate_tags, reasoning = self.nl_search_service.search(
                query
            )
            self.logger.log_tool_action(
                agent_session_id=session_id,
                tool="search_resources",
                params={"query": query},
                result_summary=f"Found {len(resource_items)} results",
            )

            if not resource_items:
                return "No resources found matching the query."

            # Format results as string for the agent
            results = []
            for item in resource_items[:5]:
                results.append(f"- {item.name}: {item.summary or 'No summary'} (Link: {item.link})")
            return "\n".join(results)

        except Exception as e:
            self.logger.log_tool_action(
                agent_session_id=session_id,
                tool="search_resources",
                params={"query": query},
                result_summary=f"Error: {e}",
            )
            return f"Error searching resources: {e}"

    def _validate_resource_tool(self, url: str) -> bool:
        """Tool function for resource validation (called by DSPy ReAct).

        Args:
            url: Resource URL to validate.

        Returns:
            Boolean: True if resource is valid, False if hallucinated/invalid.

        Raises:
            Exception: Logged as ERROR, resource treated as invalid (returns False).
        """
        session_id = self.current_session_id or "unknown"
        try:
            is_valid = self.link_verifier.verify_link(url)
            self.logger.log_tool_action(
                agent_session_id=session_id,
                tool="validate_resource",
                params={"url": url},
                result_summary=f"Valid: {is_valid}",
            )
            return is_valid
        except Exception as e:
            self.logger.log_tool_action(
                agent_session_id=session_id,
                tool="validate_resource",
                params={"url": url},
                result_summary=f"Error: {e}",
            )
            # FR-006: Exception handling - treat as invalid
            return False

    def run(
        self,
        query: str,
        include_sources: bool = False,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """Execute the agent for a single-turn query.

        Args:
            query: User's natural language query.
            include_sources: Whether to include validated resource citations.
            max_tokens: Maximum tokens for response.

        Returns:
            Dict with 'answer', 'query', 'meta', and optionally 'resources'.
            On error, returns dict with 'error', 'code', 'query'.
        """
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        self.logger.log_session_start(session_id, query)

        # Check if agent is available
        if self.lm is None or self.react_agent is None:
            error_msg = (
                "Agent is currently unavailable. The language model backend could not be initialized. "
                "Please check that Ollama is running and the configured model is available."
            )
            self.logger.log_session_end(session_id, "tool_error", None)
            return {"error": error_msg, "code": AgentErrorCode.INTERNAL_ERROR, "query": query}

        try:
            # Run the ReAct agent
            prediction = self.react_agent(question=query)
            answer = prediction.answer

            # Extract resource citations if requested
            resources: list[ResourceCitation] = []
            if include_sources:
                # Parse the agent's reasoning trace to find validated resources
                # The agent's tool calls are logged, we can extract resource citations from there
                # For now, do a simple search to get resources mentioned in the answer
                resource_items, _, _, _ = self.nl_search_service.search(query)

                # FR-002, FR-005: Filter resources using boolean validation
                validated_resources: list[ResourceCitation] = []
                for item in resource_items[:3]:  # Top 3 results
                    try:
                        is_valid = self.link_verifier.verify_link(item.link)

                        if not is_valid:
                            # FR-003: Log hallucination at WARNING level
                            try:
                                hallucination_logger.warning(
                                    f"Hallucination detected - invalid resource: {item.link}",
                                    extra={
                                        "url": item.link,
                                        "title": item.name,
                                        "query": query,
                                        "session_id": session_id,
                                    },
                                )
                            except Exception:
                                # FR-009: Suppress logging failures
                                pass
                        else:
                            # FR-007: Preserve order of valid resources
                            validated_resources.append(
                                ResourceCitation(
                                    title=item.name,
                                    url=item.link,
                                    summary=item.summary,
                                )
                            )
                    except Exception as e:
                        # FR-006: Validation exception - treat as invalid, log at ERROR
                        try:
                            hallucination_logger.error(
                                f"Validation exception for {item.link}: {e}",
                                extra={"url": item.link, "query": query, "session_id": session_id},
                                exc_info=True,
                            )
                        except Exception:
                            # FR-009: Suppress logging failures
                            pass

                resources = validated_resources

            self.logger.log_session_end(session_id, "success", answer)

            # Build response
            response: dict[str, Any] = {
                "answer": answer,
                "query": query,
                "meta": {"experimental": True},
            }

            if include_sources and resources:
                response["resources"] = [c.model_dump() for c in resources]

            return response

        except Exception as e:
            # Handle specific error cases
            error_str = str(e).lower()

            # Check for no results scenario
            if "no resources found" in error_str or "no information" in error_str:
                answer = (
                    "I couldn't find sufficient information to answer your query. "
                    "This might be because the query is too specific, too broad, or "
                    "the relevant resources are not yet in the system. "
                    "Try rephrasing your query or making it more specific."
                )
                self.logger.log_session_end(session_id, "no_evidence", answer)
                return {"answer": answer, "query": query, "meta": {"experimental": True}}

            # Unexpected error
            error_msg = "An unexpected error occurred while processing your query."
            self.logger.log_session_end(session_id, "tool_error", None)
            self.logger.log_tool_action(
                agent_session_id=session_id,
                tool="agent_run",
                params={"query": query},
                result_summary=f"Unexpected error: {e}",
            )
            return {"error": error_msg, "code": AgentErrorCode.INTERNAL_ERROR, "query": query}
