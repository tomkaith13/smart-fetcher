"""Structured JSON-lines logger for agent tool actions.

Logs to standard output instead of a file, emitting one JSON object
per line for easy ingestion by log processors.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AgentLogger:
    """Logs agent tool actions to structured JSON lines."""

    def __init__(self, log_file: str = "agent_actions.jsonl") -> None:
        """Initialize the agent logger.

        Args:
            log_file: Deprecated; retained for backward compatibility.
        """
        # Retain attribute for backward compatibility, but do not use it
        self.log_file = Path(log_file)

        self.logger = logging.getLogger("agent_logger")
        self.logger.setLevel(logging.INFO)

        # Use a stream handler to write JSON lines to stdout.
        # Avoid adding duplicate handlers if the logger is reused.
        if not self.logger.handlers:
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setLevel(logging.INFO)
            # Ensure only the JSON message is emitted per line
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
        # Prevent propagation to root logger to avoid duplicate logs
        self.logger.propagate = False

    def log_tool_action(
        self,
        agent_session_id: str,
        tool: str,
        params: dict[str, Any],
        result_summary: str,
    ) -> None:
        """Log a tool action to JSON lines.

        Args:
            agent_session_id: Unique ID for the agent session.
            tool: Tool name (e.g., "nl_search", "validate_resource").
            params: Parameters passed to the tool.
            result_summary: Brief summary of the tool result.
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_session_id": agent_session_id,
            "tool": tool,
            "params": params,
            "result_summary": result_summary,
        }
        self.logger.info(json.dumps(log_entry))

    def log_session_start(self, agent_session_id: str, query: str) -> None:
        """Log the start of an agent session.

        Args:
            agent_session_id: Unique ID for the agent session.
            query: User query for the session.
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_session_id": agent_session_id,
            "event": "session_start",
            "query": query,
        }
        self.logger.info(json.dumps(log_entry))

    def log_session_end(
        self, agent_session_id: str, status: str, answer: str | None = None
    ) -> None:
        """Log the end of an agent session.

        Args:
            agent_session_id: Unique ID for the agent session.
            status: Session status (success, no_evidence, tool_error, timeout).
            answer: Final answer if available.
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_session_id": agent_session_id,
            "event": "session_end",
            "status": status,
            "answer": answer,
        }
        self.logger.info(json.dumps(log_entry))


# Global logger instance
_agent_logger: AgentLogger | None = None


def get_agent_logger() -> AgentLogger:
    """Get or create the global agent logger instance.

    Returns:
        The global agent logger instance.
    """
    global _agent_logger
    if _agent_logger is None:
        _agent_logger = AgentLogger()
    return _agent_logger
