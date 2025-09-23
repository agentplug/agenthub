"""Tool Registry - Singleton for managing tools and FastMCP server."""

import threading
from collections.abc import Callable
from typing import Any

from mcp.server import FastMCP

from .exceptions import ToolNameConflictError, ToolNotFoundError, ToolValidationError
from .metadata import ToolMetadata


class ToolRegistry:
    """Singleton registry for managing tools and FastMCP server."""

    _instance: "ToolRegistry | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized") or not getattr(
            self, "_initialized", False
        ):
            self.mcp_server = FastMCP("AgentHub Tools")
            self.registered_tools: dict[str, Callable] = {}
            self.tool_metadata: dict[str, ToolMetadata] = {}
            # Tool access control: agent_id -> list of allowed tool names
            self.agent_tool_access: dict[str, list[str]] = {}
            self._initialized = True

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        namespace: str = "custom",
    ) -> Callable:
        """Register a tool with the registry and FastMCP server."""
        # Validate tool name
        if not name or not isinstance(name, str):
            raise ToolValidationError("Tool name must be a non-empty string")

        if name in self.registered_tools:
            raise ToolNameConflictError(f"Tool '{name}' is already registered")

        # Validate tool function
        if not callable(func):
            raise ToolValidationError("Tool must be callable")

        # Validate function signature (allow functions with or without parameters)
        import inspect

        inspect.signature(func)  # Validate function signature
        # Allow functions with any number of parameters (including 0)

        # Register with internal registry
        self.registered_tools[name] = func

        # Create tool metadata
        metadata = ToolMetadata(
            name=name, description=description, function=func, namespace=namespace
        )
        self.tool_metadata[name] = metadata

        # Register with FastMCP server
        # Register the original function directly with FastMCP
        self.mcp_server.tool(name=name, description=description)(func)

        # Tool is now registered with FastMCP

        return func

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        # First check local registry
        local_tools = list(self.registered_tools.keys())

        # Try to discover from MCP server and combine with local tools
        try:
            import asyncio

            from mcp import ClientSession
            from mcp.client.sse import sse_client

            async def discover_tools() -> list[str]:
                try:
                    async with sse_client(url="http://localhost:8000/sse") as streams:
                        async with ClientSession(*streams) as session:
                            await session.initialize()
                            tools = await session.list_tools()
                            return [tool.name for tool in tools.tools]
                except Exception as e:
                    print(f"⚠️  MCP discovery failed: {e}")
                    return []

            # Check if we're already in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, create a task instead
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, discover_tools())
                    mcp_tools = future.result(timeout=5)  # 5 second timeout
            except RuntimeError:
                # No event loop running, safe to use asyncio.run()
                mcp_tools = asyncio.run(discover_tools())

            # Combine local and MCP tools, removing duplicates
            all_tools = list(set(local_tools + mcp_tools))
            return all_tools
        except Exception as e:
            print(f"⚠️  Could not discover tools from MCP server: {e}")
            return local_tools

    def get_tool_metadata(self, name: str) -> ToolMetadata | None:
        """Get metadata for a specific tool."""
        # First check local registry
        if name in self.tool_metadata:
            return self.tool_metadata[name]

        # If not found locally, try to get from MCP server
        try:
            import asyncio

            from mcp import ClientSession
            from mcp.client.sse import sse_client

            async def get_tool_info() -> dict[str, Any] | None:
                async with sse_client(url="http://localhost:8000/sse") as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        for tool in tools.tools:
                            if tool.name == name:
                                # Extract parameters from MCP schema
                                parameters = {}
                                if (
                                    tool.inputSchema
                                    and "properties" in tool.inputSchema
                                ):
                                    for param_name, param_info in tool.inputSchema[
                                        "properties"
                                    ].items():
                                        parameters[param_name] = {
                                            "name": param_name,
                                            "type": param_info.get("type", "Any"),
                                            "required": param_name
                                            in tool.inputSchema.get("required", []),
                                            "default": param_info.get("default", None),
                                        }

                                return {
                                    "name": tool.name,
                                    "description": tool.description or "",
                                    "function": None,  # Can't get function from MCP
                                    "namespace": "mcp",
                                    "parameters": parameters,
                                }
                        return None

            # Run the async discovery using asyncio.run()
            tool_info = asyncio.run(get_tool_info())
            if tool_info:
                return ToolMetadata(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    function=tool_info["function"],
                    namespace=tool_info["namespace"],
                    parameters=tool_info.get("parameters", {}),
                )
        except Exception as e:
            print(f"⚠️  Could not get tool metadata from MCP server: {e}")

        return None

    def get_tool_function(self, name: str) -> Callable | None:
        """Get the function for a specific tool."""
        return self.registered_tools.get(name)

    def is_tool_registered(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self.registered_tools

    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool (for testing purposes)."""
        if name in self.registered_tools:
            del self.registered_tools[name]
            del self.tool_metadata[name]
            return True
        return False

    def remove_tool(self, name: str) -> bool:
        """Remove a tool from the registry (alias for unregister_tool)."""
        return self.unregister_tool(name)

    def execute_tool(self, name: str, parameters: dict) -> Any:
        """Execute a tool with given parameters."""
        if name not in self.registered_tools:
            raise ToolNotFoundError(f"Tool '{name}' not found")

        tool_func = self.registered_tools[name]
        return tool_func(**parameters)

    def register_tool_with_metadata(self, metadata: ToolMetadata) -> None:
        """Register a tool with custom metadata."""
        if metadata.name in self.registered_tools:
            raise ToolNameConflictError(f"Tool '{metadata.name}' is already registered")

        self.registered_tools[metadata.name] = metadata.function or (lambda: None)
        self.tool_metadata[metadata.name] = metadata

    def clear_agent_tools(self, agent_id: str) -> None:
        """Clear all tools assigned to an agent."""
        if agent_id in self.agent_tool_access:
            del self.agent_tool_access[agent_id]

    def cleanup(self) -> None:
        """Clean up the registry (for testing purposes)."""
        self.registered_tools.clear()
        self.tool_metadata.clear()
        self.agent_tool_access.clear()

    def get_statistics(self) -> dict:
        """Get registry statistics."""
        tools_per_agent = {
            agent_id: len(tools) for agent_id, tools in self.agent_tool_access.items()
        }
        return {
            "total_tools": len(self.registered_tools),
            "total_agents": len(self.agent_tool_access),
            "tool_names": list(self.registered_tools.keys()),
            "agent_ids": list(self.agent_tool_access.keys()),
            "tools_per_agent": tools_per_agent,
        }

    def assign_tools_to_agent(self, agent_id: str, tool_names: list[str]) -> None:
        """Assign specific tools to an agent."""
        # Validate that all tools exist (including MCP-discovered tools)
        available_tools = self.get_available_tools()
        for tool_name in tool_names:
            if tool_name not in available_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found")

        # Assign tools to agent
        self.agent_tool_access[agent_id] = tool_names.copy()

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """Get tools assigned to a specific agent."""
        return self.agent_tool_access.get(agent_id, [])

    def can_agent_access_tool(self, agent_id: str, tool_name: str) -> bool:
        """Check if an agent can access a specific tool."""
        agent_tools = self.agent_tool_access.get(agent_id, [])
        return tool_name in agent_tools

    def get_agent_tool_metadata(self, agent_id: str) -> list[ToolMetadata]:
        """Get tool metadata for tools assigned to an agent."""
        agent_tools = self.agent_tool_access.get(agent_id, [])
        return [
            self.tool_metadata[tool_name]
            for tool_name in agent_tools
            if tool_name in self.tool_metadata
        ]


# Global registry instance
_registry = ToolRegistry()


def get_available_tools() -> list[str]:
    """Get list of available tool names."""
    return _registry.get_available_tools()


def get_mcp_server() -> FastMCP:
    """Get the FastMCP server instance."""
    return _registry.mcp_server


def get_tool_metadata(name: str) -> ToolMetadata | None:
    """Get metadata for a specific tool."""
    return _registry.get_tool_metadata(name)


def get_tool_function(name: str) -> Callable | None:
    """Get the function for a specific tool."""
    return _registry.get_tool_function(name)


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _registry


def assign_tools_to_agent(agent_id: str, tool_names: list[str]) -> None:
    """Assign specific tools to an agent."""
    _registry.assign_tools_to_agent(agent_id, tool_names)


def get_agent_tools(agent_id: str) -> list[str]:
    """Get tools assigned to a specific agent."""
    return _registry.get_agent_tools(agent_id)


def can_agent_access_tool(agent_id: str, tool_name: str) -> bool:
    """Check if an agent can access a specific tool."""
    return _registry.can_agent_access_tool(agent_id, tool_name)


def get_agent_tool_metadata(agent_id: str) -> list[ToolMetadata]:
    """Get tool metadata for tools assigned to an agent."""
    return _registry.get_agent_tool_metadata(agent_id)


def run_resources() -> None:
    """Run the MCP server"""
    mcp_server = get_mcp_server()
    mcp_server.run(transport="sse")
