"""Main solve engine orchestrator."""

import logging
import time
from typing import Any

from ...interfaces import AgentWrapperProtocol
from .custom_handler import CustomSolveHandler
from .framework_handler import FrameworkSolveHandler
from .interface import AgentSolveInterface

logger = logging.getLogger(__name__)


class SolveEngine:
    """Orchestrates intelligent solve functionality."""

    def __init__(
        self, agent_wrapper: AgentWrapperProtocol, llm_service: Any = None
    ) -> None:
        """Initialize solve engine."""
        self.agent_wrapper = agent_wrapper
        self.custom_handler = CustomSolveHandler(agent_wrapper)
        self.framework_handler = FrameworkSolveHandler(agent_wrapper, llm_service)
        self._custom_solve_agent: AgentSolveInterface | None = None

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """
        Intelligently solve a user query by selecting and executing the most
        appropriate method.

        This method implements the Phase 3.2 intelligent solve functionality:
        1. Check if agent has custom solve() method
        2. If yes, delegate to custom solve()
        3. If no, use LLM to select best method and extract parameters
        4. Execute selected method with extracted parameters

        Args:
            query: User's natural language query
            context: Optional context information (tools, knowledge, etc.)
            **kwargs: Additional parameters

        Returns:
            Result of solving the query (same format as direct method calls)
        """
        start_time = time.time()

        try:
            # Check if agent has custom solve() method
            if self._has_custom_solve():
                return self.custom_handler.solve(query, context, **kwargs)
            else:
                return self.framework_handler.solve(query, context, **kwargs)

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in solve() method: {e}")
            # Return error in the same format as agent execution errors
            return {"error": str(e), "execution_time": execution_time}

    def _has_custom_solve(self) -> bool:
        """Check if agent has a custom solve() method."""
        try:
            if self._custom_solve_agent is None:
                # Try to load the agent and check for solve method
                self._custom_solve_agent = self._load_custom_solve_agent()

            return self._custom_solve_agent is not None

        except Exception as e:
            logger.debug(f"Could not check for custom solve method: {e}")
            return False

    def _load_custom_solve_agent(self) -> AgentSolveInterface | None:
        """Load custom solve agent if available."""
        try:
            if not self.agent_wrapper.runtime:
                return None

            # Try to import and instantiate the agent
            # This is a simplified approach - in practice, you'd need more robust
            # loading
            agent_module = self._load_agent_module()
            if agent_module and hasattr(agent_module, "solve"):
                # Check if it implements the interface
                if isinstance(agent_module, AgentSolveInterface):
                    return agent_module
                elif callable(getattr(agent_module, "solve", None)):
                    # Create a wrapper for non-interface agents
                    from .custom_handler import CustomSolveWrapper

                    return CustomSolveWrapper(agent_module)

            return None

        except Exception as e:
            logger.debug(f"Could not load custom solve agent: {e}")
            return None

    def _load_agent_module(self) -> Any:
        """Load the agent module dynamically."""
        try:
            # This is a simplified approach - in practice, you'd need more robust
            # loading logic
            agent_path = self.agent_wrapper.agent_info.path
            if not agent_path:
                return None

            # For now, return None - this would need proper module loading
            return None

        except Exception as e:
            logger.debug(f"Could not load agent module: {e}")
            return None

    def get_solve_capabilities(self) -> dict[str, Any]:
        """Get solve capabilities information."""
        if self._has_custom_solve():
            return self.custom_handler.get_solve_capabilities()
        else:
            return {
                "has_custom_solve": False,
                "description": "Framework-level solve using LLM method selection",
                "version": "1.0.0",
            }
