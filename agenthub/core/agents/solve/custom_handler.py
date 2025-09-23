"""Handles custom agent solve methods."""

import logging
from typing import Any

from .interface import AgentSolveInterface

logger = logging.getLogger(__name__)


class CustomSolveHandler:
    """Handles agents with custom solve implementations."""

    def __init__(self, agent_wrapper: Any) -> None:
        """Initialize custom solve handler."""
        self.agent_wrapper = agent_wrapper

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Execute custom solve method."""
        try:
            # Get the custom solve agent
            custom_agent = getattr(
                self.agent_wrapper.solve_engine, "_custom_solve_agent", None
            )
            if not custom_agent:
                raise RuntimeError("No custom solve agent available")

            # Prepare context
            full_context = self._prepare_solve_context(context)

            # Execute custom solve
            result = custom_agent.solve(query, full_context, **kwargs)

            # Return the exact same format as direct method calls
            return result

        except Exception as e:
            logger.error(f"Error in custom solve method: {e}")
            return {"error": str(e), "execution_time": 0.0}

    def _prepare_solve_context(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Prepare context for custom solve."""
        full_context = context or {}

        # Add tool context
        full_context["available_tools"] = self.agent_wrapper.get_all_available_tools()
        full_context["tool_descriptions"] = self.agent_wrapper.get_tool_context_json()

        # Add knowledge context
        if self.agent_wrapper.is_knowledge_available():
            full_context["knowledge"] = self.agent_wrapper.get_knowledge()

        # Add agent info
        full_context["agent_info"] = {
            "name": self.agent_wrapper.agent_info.name,
            "namespace": self.agent_wrapper.agent_info.namespace,
            "methods": self.agent_wrapper.agent_info.methods,
        }

        return full_context

    def get_solve_capabilities(self) -> dict[str, Any]:
        """Get solve capabilities from the custom agent."""
        custom_agent = getattr(
            self.agent_wrapper.solve_engine, "_custom_solve_agent", None
        )
        if custom_agent and hasattr(custom_agent, "get_solve_capabilities"):
            capabilities = custom_agent.get_solve_capabilities()
            return (
                capabilities
                if isinstance(capabilities, dict)
                else {
                    "has_custom_solve": True,
                    "description": "Custom solve method implementation",
                    "version": "1.0.0",
                }
            )
        return {
            "has_custom_solve": True,
            "description": "Custom solve method implementation",
            "version": "1.0.0",
        }


class CustomSolveWrapper(AgentSolveInterface):
    """Wrapper for agents with custom solve methods."""

    def __init__(self, agent_instance: Any) -> None:
        """Initialize wrapper."""
        self.agent_instance = agent_instance

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Delegate to the agent's custom solve method."""
        result = self.agent_instance.solve(query, context, **kwargs)
        return result

    def get_solve_capabilities(self) -> dict[str, Any]:
        """Get solve capabilities from the wrapped agent."""
        if hasattr(self.agent_instance, "get_solve_capabilities"):
            capabilities = self.agent_instance.get_solve_capabilities()
            return (
                capabilities
                if isinstance(capabilities, dict)
                else {
                    "has_custom_solve": True,
                    "description": "Custom solve method (wrapped)",
                    "version": "1.0.0",
                }
            )
        return {
            "has_custom_solve": True,
            "description": "Custom solve method (wrapped)",
            "version": "1.0.0",
        }
