"""Agent Tool Manager - Manages tool assignment and execution for agents.

This module provides the AgentToolManager class that handles:
- Tool assignment to specific agents
- Agent-specific tool access control
- Tool execution through MCP client
- Tool discovery for agents
"""

import asyncio
import json
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from agenthub.core.tools import (
    ToolAccessDeniedError,
    ToolNotFoundError,
    get_tool_registry,
)


class AgentToolManager:
    """Manages tool assignment and execution for agents."""

    def __init__(self):
        """Initialize the agent tool manager."""
        self.tool_registry = get_tool_registry()
        self.agent_tools: dict[str, set[str]] = {}  # agent_id -> set of tool names
        self.client: ClientSession | None = None
        self._client_lock = asyncio.Lock()

    async def _ensure_client(self) -> ClientSession:
        """Ensure MCP client is connected."""
        async with self._client_lock:
            if self.client is None:
                # Create MCP client connection to our FastMCP server
                server_params = StdioServerParameters(
                    command="python",
                    args=[
                        "-c",
                        "from agenthub.core.tools import get_mcp_server; "
                        "import asyncio; asyncio.run(get_mcp_server().run_stdio())",
                    ],
                )

                stdio_transport = stdio_client(server_params)
                self.client = await stdio_transport.__aenter__()

            return self.client

    def assign_tools_to_agent(self, agent_id: str, tool_names: list[str]) -> list[str]:
        """Assign tools to a specific agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_names: List of tool names to assign

        Returns:
            List of successfully assigned tool names

        Raises:
            ToolNotFoundError: If any tool name doesn't exist
        """
        available_tools = self.tool_registry.get_available_tools()
        assigned_tools = []

        for tool_name in tool_names:
            if tool_name not in available_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")
            assigned_tools.append(tool_name)

        # Store assigned tools for this agent
        self.agent_tools[agent_id] = set(assigned_tools)

        return assigned_tools

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """Get list of tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of tool names assigned to the agent
        """
        return list(self.agent_tools.get(agent_id, set()))

    def has_tool_access(self, agent_id: str, tool_name: str) -> bool:
        """Check if agent has access to a specific tool.

        Args:
            agent_id: Unique identifier for the agent
            tool_name: Name of the tool to check

        Returns:
            True if agent has access to the tool
        """
        return tool_name in self.agent_tools.get(agent_id, set())

    async def execute_tool(
        self, agent_id: str, tool_name: str, arguments: dict[str, Any]
    ) -> str:
        """Execute a tool on behalf of an agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            JSON string result from tool execution

        Raises:
            ToolAccessDeniedError: If agent doesn't have access to the tool
            ToolNotFoundError: If tool doesn't exist
        """
        # Check if agent has access to this tool
        if not self.has_tool_access(agent_id, tool_name):
            raise ToolAccessDeniedError(
                f"Agent '{agent_id}' does not have access to tool '{tool_name}'"
            )

        # Check if tool exists
        available_tools = self.tool_registry.get_available_tools()
        if tool_name not in available_tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")

        try:
            # Get MCP client and execute tool
            client = await self._ensure_client()

            # Call tool through MCP
            result = await client.call_tool(tool_name, arguments)

            # Convert result to JSON string
            if result and len(result) > 0:
                return result[0].text if hasattr(result[0], "text") else str(result[0])
            else:
                return json.dumps({"error": "No result returned from tool"})

        except Exception as e:
            return json.dumps(
                {
                    "error": f"Tool execution failed: {str(e)}",
                    "tool_name": tool_name,
                    "agent_id": agent_id,
                }
            )

    def remove_agent_tools(self, agent_id: str) -> bool:
        """Remove all tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            True if agent had tools assigned, False otherwise
        """
        if agent_id in self.agent_tools:
            del self.agent_tools[agent_id]
            return True
        return False

    def get_all_agent_tools(self) -> dict[str, list[str]]:
        """Get all agent tool assignments.

        Returns:
            Dictionary mapping agent_id to list of assigned tool names
        """
        return {agent_id: list(tools) for agent_id, tools in self.agent_tools.items()}

    async def close(self):
        """Close the MCP client connection."""
        if self.client:
            await self.client.close()
            self.client = None


# Global instance
_tool_manager: AgentToolManager | None = None


def get_tool_manager() -> AgentToolManager:
    """Get the global tool manager instance."""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = AgentToolManager()
    return _tool_manager
