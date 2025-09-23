"""Unified Agent Tool Manager - Manages both built-in and external tools for agents.

This module provides the AgentToolManager class that handles:
- Built-in tool management from agent.yaml
- External tool assignment and access control
- Tool execution through MCP client
- Tool discovery and validation
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from agenthub.core.tools import (
    ToolAccessDeniedError,
    ToolNotFoundError,
    get_tool_registry,
)
from agenthub.core.tools.exceptions import ToolConflictError

logger = logging.getLogger(__name__)


@dataclass
class BuiltinToolInfo:
    """Information about a built-in tool."""

    name: str
    description: str
    required: bool  # True = cannot be disabled, False = can be disabled
    parameters: dict[str, Any]
    enabled: bool = True


class AgentToolManager:
    """Unified tool manager for both built-in and external tools."""

    def __init__(self, agent_manifest: dict[str, Any] | None = None):
        """Initialize the unified agent tool manager."""
        self.tool_registry = get_tool_registry()
        self.agent_tools: dict[str, set[str]] = (
            {}
        )  # agent_id -> set of external tool names
        self.client: ClientSession | None = None
        self._client_lock = asyncio.Lock()

        # Built-in tool management
        self.builtin_tools: dict[str, BuiltinToolInfo] = {}
        self.disabled_tools: set[str] = set()

        if agent_manifest:
            self._load_builtin_tools_from_manifest(agent_manifest)

    def _load_builtin_tools_from_manifest(self, manifest: dict[str, Any]) -> None:
        """Load built-in tools from agent.yaml builtin_tools section."""
        builtin_tools_config = manifest.get("builtin_tools", {})

        for tool_name, tool_config in builtin_tools_config.items():
            self.builtin_tools[tool_name] = BuiltinToolInfo(
                name=tool_name,
                description=tool_config.get("description", ""),
                required=tool_config.get("required", False),
                parameters=tool_config.get("parameters", {}),
            )

        logger.debug(
            f"Loaded {len(self.builtin_tools)} built-in tools: "
            f"{list(self.builtin_tools.keys())}"
        )

    def disable_builtin_tools(self, tool_names: list[str]) -> None:
        """Disable specified built-in tools."""
        for tool_name in tool_names:
            if tool_name in self.builtin_tools:
                tool_info = self.builtin_tools[tool_name]
                if tool_info.required:
                    raise ValueError(
                        f"Built-in tool '{tool_name}' cannot be disabled "
                        f"(required core functionality)"
                    )
                self.disabled_tools.add(tool_name)
                tool_info.enabled = False
                logger.info(f"Disabled built-in tool: {tool_name}")
            else:
                logger.warning(
                    f"Attempted to disable unknown built-in tool: {tool_name}"
                )

    def enable_builtin_tools(self, tool_names: list[str]) -> None:
        """Enable specified built-in tools."""
        for tool_name in tool_names:
            if tool_name in self.builtin_tools:
                self.disabled_tools.discard(tool_name)
                self.builtin_tools[tool_name].enabled = True
                logger.info(f"Enabled built-in tool: {tool_name}")
            else:
                logger.warning(
                    f"Attempted to enable unknown built-in tool: {tool_name}"
                )

    def get_available_builtin_tools(self) -> list[str]:
        """Get list of available (enabled) built-in tools."""
        return [name for name, tool in self.builtin_tools.items() if tool.enabled]

    def is_builtin_tool_available(self, tool_name: str) -> bool:
        """Check if a built-in tool is available (enabled)."""
        tool_info = self.builtin_tools.get(tool_name)
        return tool_info is not None and tool_info.enabled

    def is_builtin_tool_required(self, tool_name: str) -> bool:
        """Check if a built-in tool is required (cannot be disabled)."""
        tool_info = self.builtin_tools.get(tool_name)
        return tool_info is not None and tool_info.required

    def validate_builtin_tool_parameters(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> list[str]:
        """Validate parameters for a built-in tool."""
        tool_info = self.builtin_tools.get(tool_name)
        if not tool_info:
            return [f"Tool '{tool_name}' not found"]

        errors = []
        tool_params = tool_info.parameters

        # Check required parameters
        for param_name, param_config in tool_params.items():
            if param_config.get("required", False) and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")

        # Validate provided parameters
        for param_name, param_value in parameters.items():
            if param_name in tool_params:
                param_config = tool_params[param_name]
                param_errors = self._validate_parameter(
                    param_name, param_value, param_config
                )
                errors.extend(param_errors)
            else:
                errors.append(
                    f"Unknown parameter '{param_name}' for tool '{tool_name}'"
                )

        return errors

    def _validate_parameter(
        self, param_name: str, param_value: Any, param_config: dict[str, Any]
    ) -> list[str]:
        """Validate a single parameter."""
        errors = []

        # Type validation
        expected_type = param_config.get("type", "string")
        if not self._validate_parameter_type(param_value, expected_type):
            errors.append(
                f"Parameter '{param_name}' should be {expected_type}, "
                f"got {type(param_value).__name__}"
            )

        # Enum validation
        if "enum" in param_config:
            if param_value not in param_config["enum"]:
                errors.append(
                    f"Parameter '{param_name}' must be one of "
                    f"{param_config['enum']}, got '{param_value}'"
                )

        return errors

    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }

        expected_python_type = type_mapping.get(expected_type, str)
        if expected_python_type is None:
            return False
        # Use type() instead of isinstance for better type checking
        return type(value) is expected_python_type

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
        """Assign external tools to a specific agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_names: List of external tool names to assign

        Returns:
            List of successfully assigned tool names

        Raises:
            ToolNotFoundError: If any tool name doesn't exist
            ToolConflictError: If tool conflicts with built-in tools
        """
        available_tools = self.tool_registry.get_available_tools()
        assigned_tools = []

        for tool_name in tool_names:
            # Check for conflicts with built-in tools
            if tool_name in self.builtin_tools:
                raise ToolConflictError(
                    f"Tool '{tool_name}' conflicts with built-in tool. "
                    f"Use disable_builtin_tools() to disable it first.",
                    tool_name=tool_name,
                    conflict_type="builtin_conflict",
                )

            if tool_name not in available_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")
            assigned_tools.append(tool_name)

        # Store assigned tools for this agent
        self.agent_tools[agent_id] = set(assigned_tools)

        return assigned_tools

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """Get list of external tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of external tool names assigned to the agent
        """
        return list(self.agent_tools.get(agent_id, set()))

    def get_all_available_tools(self, agent_id: str) -> list[str]:
        """Get all available tools for an agent (built-in + external).

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of all available tool names
        """
        available = self.get_available_builtin_tools()
        available.extend(self.get_agent_tools(agent_id))
        return available

    def has_tool_access(self, agent_id: str, tool_name: str) -> bool:
        """Check if agent has access to a specific tool (built-in or external).

        Args:
            agent_id: Unique identifier for the agent
            tool_name: Name of the tool to check

        Returns:
            True if agent has access to the tool
        """
        # Check built-in tools first
        if self.is_builtin_tool_available(tool_name):
            return True

        # Check external tools
        return tool_name in self.agent_tools.get(agent_id, set())

    async def execute_tool(
        self, agent_id: str, tool_name: str, arguments: dict[str, Any]
    ) -> str:
        """Execute a tool on behalf of an agent (built-in or external).

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

        # Handle built-in tools
        if tool_name in self.builtin_tools:
            if not self.is_builtin_tool_available(tool_name):
                raise ToolAccessDeniedError(f"Built-in tool '{tool_name}' is disabled")

            # Validate parameters for built-in tools
            errors = self.validate_builtin_tool_parameters(tool_name, arguments)
            if errors:
                return json.dumps(
                    {"error": f"Parameter validation failed: {'; '.join(errors)}"}
                )

            # For built-in tools, we would typically execute through the agent runtime
            # For now, return a placeholder response
            return json.dumps(
                {
                    "result": (
                        f"Built-in tool '{tool_name}' executed with arguments: "
                        f"{arguments}"
                    ),
                    "tool_type": "builtin",
                }
            )

        # Handle external tools through MCP
        available_tools = self.tool_registry.get_available_tools()
        if tool_name not in available_tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")

        try:
            # Get MCP client and execute tool
            client = await self._ensure_client()

            # Call tool through MCP
            result = await client.call_tool(tool_name, arguments)

            # Convert result to JSON string
            if result and hasattr(result, "content") and len(result.content) > 0:
                return (
                    result.content[0].text
                    if hasattr(result.content[0], "text")
                    else str(result.content[0])
                )
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
            Dictionary mapping agent_id to list of assigned external tool names
        """
        return {agent_id: list(tools) for agent_id, tools in self.agent_tools.items()}

    def get_tool_summary(self, agent_id: str) -> dict[str, Any]:
        """Get comprehensive tool summary for an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Dictionary with tool summary information
        """
        total_builtin = len(self.builtin_tools)
        enabled_builtin = len(self.get_available_builtin_tools())
        disabled_builtin = len(self.disabled_tools)
        required_builtin = len([t for t in self.builtin_tools.values() if t.required])
        optional_builtin = total_builtin - required_builtin
        external_tools = len(self.get_agent_tools(agent_id))

        return {
            "builtin_tools": {
                "total": total_builtin,
                "enabled": enabled_builtin,
                "disabled": disabled_builtin,
                "required": required_builtin,
                "optional": optional_builtin,
                "names": list(self.builtin_tools.keys()),
                "enabled_names": self.get_available_builtin_tools(),
                "disabled_names": list(self.disabled_tools),
            },
            "external_tools": {
                "count": external_tools,
                "names": self.get_agent_tools(agent_id),
            },
            "all_available": self.get_all_available_tools(agent_id),
        }

    async def close(self) -> None:
        """Close the MCP client connection."""
        if self.client:
            if hasattr(self.client, "close"):
                await self.client.close()
            elif hasattr(self.client, "aclose"):
                await self.client.aclose()
            self.client = None


# Global instance
_tool_manager: AgentToolManager | None = None


def get_tool_manager() -> AgentToolManager:
    """Get the global tool manager instance."""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = AgentToolManager()
    return _tool_manager
