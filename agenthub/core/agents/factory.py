"""Agent factory with dependency injection."""

import logging
from typing import Any

from ..interfaces import (
    KnowledgeManagerProtocol,
    ToolManagerProtocol,
)
from .wrapper import AgentWrapper

logger = logging.getLogger(__name__)


class AgentWrapperFactory:
    """Factory for creating agent wrappers with dependency injection."""

    def __init__(self) -> None:
        """Initialize factory."""

    def create_wrapper(
        self,
        agent_info: dict,
        tool_registry: Any = None,
        agent_id: str | None = None,
        assigned_tools: list[str] | None = None,
        runtime: Any = None,
    ) -> AgentWrapper:
        """Create agent wrapper with injected dependencies."""

        # Get dependencies from container
        knowledge_manager = self._get_knowledge_manager()
        tool_manager = self._get_tool_manager(agent_info)

        return AgentWrapper(
            agent_info=agent_info,
            tool_registry=tool_registry,
            agent_id=agent_id,
            assigned_tools=assigned_tools,
            runtime=runtime,
            knowledge_manager=knowledge_manager,
            tool_manager=tool_manager,
        )

    def _get_knowledge_manager(self) -> KnowledgeManagerProtocol | None:
        """Construct the knowledge manager (optional feature boundary)."""
        try:
            from ..knowledge import KnowledgeManager

            return KnowledgeManager()
        except ImportError as e:
            logger.warning(f"Knowledge manager unavailable: {e}", exc_info=True)
            return None

    def _get_tool_manager(self, agent_info: dict) -> ToolManagerProtocol | None:
        """Construct the tool manager (optional feature boundary)."""
        try:
            from ..mcp.agent_tool_manager import AgentToolManager

            return AgentToolManager(agent_info.get("manifest", {}))
        except ImportError as e:
            logger.warning(f"Tool manager unavailable: {e}", exc_info=True)
            return None


# Global factory instance
_factory: AgentWrapperFactory | None = None


def get_agent_wrapper_factory() -> AgentWrapperFactory:
    """Get the global agent wrapper factory."""
    global _factory
    if _factory is None:
        _factory = AgentWrapperFactory()
    return _factory
