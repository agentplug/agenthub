"""Agent factory with dependency injection."""

from typing import Any

from ..di import get_container
from ..interfaces import (
    KnowledgeManagerProtocol,
    ToolManagerProtocol,
)
from .wrapper import AgentWrapper


class AgentWrapperFactory:
    """Factory for creating agent wrappers with dependency injection."""

    def __init__(self) -> None:
        """Initialize factory."""
        self.container = get_container()

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
        """Get knowledge manager from container."""
        try:
            return self.container.get(KnowledgeManagerProtocol)  # type: ignore[type-abstract]
        except ValueError:
            return None

    def _get_tool_manager(self, agent_info: dict) -> ToolManagerProtocol | None:
        """Get tool manager from container."""
        try:
            # For now, create tool manager directly since it needs agent_info
            from ..mcp.agent_tool_manager import AgentToolManager

            return AgentToolManager(agent_info.get("manifest", {}))
        except ImportError:
            return None


# Global factory instance
_factory: AgentWrapperFactory | None = None


def get_agent_wrapper_factory() -> AgentWrapperFactory:
    """Get the global agent wrapper factory."""
    global _factory
    if _factory is None:
        _factory = AgentWrapperFactory()
    return _factory
