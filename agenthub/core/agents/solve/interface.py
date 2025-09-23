"""
Agent Solve Interface for Phase 3.2 Intelligent Solve Method

Defines the interface that agents can implement for custom solve() methods.
"""

from abc import ABC, abstractmethod
from typing import Any


class AgentSolveInterface(ABC):
    """
    Abstract interface for custom agent solve() methods.

    Agents can implement this interface to provide their own intelligent
    solve() method that will be called by the framework instead of using
    the default LLM-based method selection.
    """

    @abstractmethod
    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """
        Solve a user query using the agent's custom logic.

        Args:
            query: User's natural language query
            context: Optional context information (tools, knowledge, etc.)
            **kwargs: Additional parameters

        Returns:
            Result of solving the query

        Raises:
            NotImplementedError: If the agent doesn't implement this method
            AgentExecutionError: If there's an error during execution
        """
        raise NotImplementedError("Subclasses must implement solve method")

    def get_solve_capabilities(self) -> dict[str, Any]:
        """
        Get information about the agent's solve capabilities.

        Returns:
            Dictionary describing the agent's solve capabilities
        """
        return {
            "has_custom_solve": True,
            "description": "Custom solve method implementation",
            "version": "1.0.0",
        }

    def validate_solve_input(
        self, query: str, context: dict[str, Any] | None = None
    ) -> bool:
        """
        Validate input for the solve method.

        Args:
            query: User's natural language query
            context: Optional context information

        Returns:
            True if input is valid, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
        # context is already typed as dict[str, Any] | None, so no need to check
        return True

    def get_solve_help(self) -> str:
        """
        Get help information for the solve method.

        Returns:
            Help text describing how to use the solve method
        """
        return (
            "This agent provides a custom solve() method that can intelligently "
            "handle natural language queries. The method will analyze your query "
            "and determine the best approach to solve it using the agent's "
            "available methods and capabilities."
        )
