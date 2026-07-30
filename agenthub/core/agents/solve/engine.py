"""Main solve engine orchestrator."""

import logging
import time
from typing import Any

from ...interfaces import AgentWrapperProtocol
from .framework_handler import FrameworkSolveHandler

logger = logging.getLogger(__name__)


class SolveEngine:
    """Orchestrates intelligent solve functionality.

    solve() uses LLM method selection over the agent's manifest interface.
    An agent that exposes its own ``solve`` method needs no special path:
    the framework selects and invokes it like any other declared method.
    (A separate never-functional "custom solve" loading mechanism was
    removed; it always resolved to None.)
    """

    def __init__(
        self, agent_wrapper: AgentWrapperProtocol, llm_service: Any = None
    ) -> None:
        """Initialize solve engine."""
        self.agent_wrapper = agent_wrapper
        self.framework_handler = FrameworkSolveHandler(agent_wrapper, llm_service)

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """
        Intelligently solve a user query: the LLM selects the most
        appropriate method from the agent's interface and extracts its
        parameters.

        Args:
            query: User's natural language query
            context: Optional context information (tools, knowledge, etc.)
            **kwargs: Additional parameters

        Returns:
            Result of solving the query (same format as direct method calls)
        """
        start_time = time.time()

        try:
            return self.framework_handler.solve(query, context, **kwargs)
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in solve() method: {e}", exc_info=True)
            # Boundary: errors become the result-dict contract callers
            # expect. (Raising typed errors instead is a planned breaking
            # change tracked with the public-API-contract work.)
            return {"error": str(e), "execution_time": execution_time}

    def get_solve_capabilities(self) -> dict[str, Any]:
        """Get solve capabilities information."""
        return {
            "has_custom_solve": False,
            "description": "Framework-level solve using LLM method selection",
            "version": "1.0.0",
        }
