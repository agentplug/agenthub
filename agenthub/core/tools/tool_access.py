"""Tool Access Control Module.

This module handles agent-tool access control and permissions.
"""

from typing import Any

from .exceptions import ToolNotFoundError
from .metadata import ToolMetadata


class ToolAccessManager:
    """
    Manages agent-tool access control and permissions.

    Responsibilities:
    - Tracking which tools are assigned to which agents
    - Validating agent-tool access permissions
    - Managing tool access metadata
    """

    def __init__(self) -> None:
        """Initialize the tool access manager."""
        # Tool access control: agent_id -> list of allowed tool names
        self.agent_tool_access: dict[str, list[str]] = {}

    def assign_tools(
        self, agent_id: str, tool_names: list[str], available_tools: list[str]
    ) -> None:
        """
        Assign specific tools to an agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_names: List of tool names to assign
            available_tools: List of currently available tools for validation

        Raises:
            ToolNotFoundError: If any tool doesn't exist
        """
        # Validate that all tools exist
        for tool_name in tool_names:
            if tool_name not in available_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found")

        # Assign tools to agent
        self.agent_tool_access[agent_id] = tool_names.copy()

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """
        Get tools assigned to a specific agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of tool names assigned to the agent (empty if none)
        """
        return self.agent_tool_access.get(agent_id, [])

    def can_access(self, agent_id: str, tool_name: str) -> bool:
        """
        Check if an agent can access a specific tool.

        Args:
            agent_id: Unique identifier for the agent
            tool_name: Name of the tool to check

        Returns:
            True if agent can access the tool, False otherwise
        """
        agent_tools = self.agent_tool_access.get(agent_id, [])
        return tool_name in agent_tools

    def clear_agent_tools(self, agent_id: str) -> None:
        """
        Clear all tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        if agent_id in self.agent_tool_access:
            del self.agent_tool_access[agent_id]

    def get_agent_tool_metadata(
        self, agent_id: str, tool_metadata_dict: dict[str, ToolMetadata] | None = None
    ) -> list[ToolMetadata]:
        """
        Get tool metadata for tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_metadata_dict: Optional dictionary of all tool metadata

        Returns:
            List of ToolMetadata for tools assigned to the agent
        """
        agent_tools = self.agent_tool_access.get(agent_id, [])

        if tool_metadata_dict is None:
            return []

        return [
            tool_metadata_dict[tool_name]
            for tool_name in agent_tools
            if tool_name in tool_metadata_dict
        ]

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about tool access control.

        Returns:
            Dictionary with access control statistics
        """
        tools_per_agent = {
            agent_id: len(tools) for agent_id, tools in self.agent_tool_access.items()
        }
        return {
            "total_agents": len(self.agent_tool_access),
            "agent_ids": list(self.agent_tool_access.keys()),
            "tools_per_agent": tools_per_agent,
        }
