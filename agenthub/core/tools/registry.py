"""Tool Registry - Core tool registration and management.

This module provides the core ToolRegistry class which manages tool
registration, storage, and metadata. It delegates MCP server management
and access control to specialized modules.
"""

import threading
from collections.abc import Callable
from typing import Any

# Try to import FastMCP, fallback to MCPServer if not available
try:
    from mcp.server import FastMCP
except ImportError:
    try:
        from chuk_mcp.server import MCPServer as FastMCP
    except ImportError:
        FastMCP = None  # type: ignore[assignment]

from .exceptions import (
    ToolExecutionError,
    ToolNameConflictError,
    ToolNotFoundError,
    ToolValidationError,
)
from .mcp_server import MCPServerManager
from .metadata import ToolMetadata
from .tool_access import ToolAccessManager


class ToolRegistry:
    """
    Core tool registry for managing tools and their metadata.

    This is the central registry for tool management. It handles:
    - Tool registration and storage
    - Tool metadata management
    - Tool discovery and retrieval

    MCP server management and access control are delegated to
    specialized components (MCPServerManager and ToolAccessManager).
    """

    _instance: "ToolRegistry | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern - ensure only one registry instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the tool registry."""
        if not hasattr(self, "_initialized") or not getattr(
            self, "_initialized", False
        ):
            # Core tool storage
            self.registered_tools: dict[str, Callable] = {}
            self.tool_metadata: dict[str, ToolMetadata] = {}

            # Delegate MCP server management to specialized component
            self.mcp_manager = MCPServerManager()

            # Delegate access control to specialized component
            self.access_manager = ToolAccessManager()

            self._initialized = True

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        namespace: str = "custom",
    ) -> Callable:
        """
        Register a tool with the registry and MCP server.

        Args:
            name: Tool name (must be unique)
            func: Callable function to register as a tool
            description: Tool description
            namespace: Tool namespace (default: "custom")

        Returns:
            The decorated function

        Raises:
            ToolValidationError: If tool name or function is invalid
            ToolNameConflictError: If tool name already registered
        """
        # Validate tool name
        if not name or not isinstance(name, str):
            raise ToolValidationError("Tool name must be a non-empty string")

        if name in self.registered_tools:
            raise ToolNameConflictError(f"Tool '{name}' is already registered")

        # Validate tool function
        if not callable(func):
            raise ToolValidationError("Tool must be callable")

        # Validate function signature
        import inspect

        inspect.signature(func)  # Validate function signature

        # Register with internal registry
        self.registered_tools[name] = func

        # Create tool metadata
        metadata = ToolMetadata(
            name=name, description=description, function=func, namespace=namespace
        )
        self.tool_metadata[name] = metadata

        # Register with MCP server (if available)
        mcp_server = self.mcp_manager.get_server()
        if mcp_server is not None:
            # Handle different MCP server APIs
            if hasattr(mcp_server, "tool"):
                # FastMCP API - use decorator style
                mcp_server.tool(name=name, description=description)(func)
            elif hasattr(mcp_server, "register_tool"):
                # MCPServer API (chuk-mcp) - needs handler and schema
                mcp_server.register_tool(
                    name=name,
                    handler=func,
                    schema={},
                    description=description,
                )

        return func

    def register_tool_with_metadata(self, metadata: ToolMetadata) -> ToolMetadata:
        """
        Register a tool using a complete metadata object.

        This maintains backwards compatibility with the legacy ToolRegistry API
        expected by the phase 2.5 test suites.
        """
        if metadata.function is None:
            raise ToolValidationError(
                "Tool metadata must include a callable function reference"
            )

        self.register_tool(
            metadata.name,
            metadata.function,
            metadata.description,
            metadata.namespace,
        )

        # Preserve any custom parameter / return metadata supplied by callers.
        self.tool_metadata[metadata.name] = metadata
        return metadata

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool from the registry.

        Args:
            name: Tool name to unregister

        Returns:
            True if tool was found and unregistered, False otherwise
        """
        if name in self.registered_tools:
            del self.registered_tools[name]
            del self.tool_metadata[name]
            return True
        return False

    # Backwards compatible alias used throughout the legacy tests.
    def remove_tool(self, name: str) -> bool:
        """Alias for unregister_tool, kept for compatibility."""
        return self.unregister_tool(name)

    def get_tool_function(self, name: str) -> Callable | None:
        """
        Get the function for a specific tool.

        Args:
            name: Tool name

        Returns:
            Callable function or None if not found
        """
        return self.registered_tools.get(name)

    def get_tool_metadata(self, name: str) -> ToolMetadata | None:
        """
        Get metadata for a specific tool.

        Args:
            name: Tool name

        Returns:
            ToolMetadata or None if not found
        """
        local_metadata = self.tool_metadata.get(name)
        if local_metadata is not None:
            return local_metadata

        for metadata in self._discover_mcp_tool_metadata():
            if metadata.name == name:
                # Cache discovered metadata so subsequent calls are fast.
                self.tool_metadata[name] = metadata
                return metadata
        return None

    def is_tool_registered(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool is registered, False otherwise
        """
        return name in self.registered_tools

    def _discover_mcp_tool_metadata(self) -> list[ToolMetadata]:
        """Discover tool metadata exposed via the MCP server."""
        try:
            import asyncio
        except ImportError:  # pragma: no cover
            return []

        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client
        except ImportError:
            try:
                from chuk_mcp import ClientSession  # type: ignore
                from chuk_mcp.client.sse import sse_client  # type: ignore
            except ImportError:
                return []

        host, port = self.mcp_manager.get_config()
        sse_url = f"http://{host}:{port}/sse"

        async def discover_tools() -> list[ToolMetadata]:
            try:
                async with sse_client(url=sse_url) as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        return [
                            ToolMetadata(
                                name=getattr(tool, "name", "unknown"),
                                description=getattr(tool, "description", ""),
                                function=None,
                                namespace="mcp",
                            )
                            for tool in getattr(tools, "tools", [])
                        ]
            except Exception as e:
                print(f"⚠️  MCP discovery failed from {sse_url}: {e}")
                return []

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(discover_tools())

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, discover_tools())
            return future.result(timeout=5)

    def get_available_tools(self) -> list[str]:
        """
        Get list of available tool names.
        """
        local_tools = list(self.registered_tools.keys())
        try:
            mcp_metadata = self._discover_mcp_tool_metadata()
        except Exception as e:  # pragma: no cover
            print(f"⚠️  Could not discover tools from MCP server: {e}")
            mcp_metadata = []

        remote_names = [metadata.name for metadata in mcp_metadata]
        return list({*local_tools, *remote_names})

    def execute_tool(self, name: str, parameters: dict[str, Any] | None = None) -> Any:
        """
        Execute a registered tool by name.

        Args:
            name: Registered tool name
            parameters: Keyword arguments to pass to the tool
        """
        parameters = parameters or {}
        func = self.get_tool_function(name)
        if func is None:
            raise ToolNotFoundError(f"Tool '{name}' not found")

        import inspect

        try:
            if inspect.iscoroutinefunction(func):
                import asyncio

                async def _run_async() -> Any:
                    return await func(**parameters)

                try:
                    asyncio.get_running_loop()
                except RuntimeError:
                    return asyncio.run(_run_async())
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(_run_async())
                finally:
                    new_loop.close()
            return func(**parameters)
        except TypeError:
            # Allow TypeError to bubble up for invalid signatures (tests assert this)
            raise
        except ToolNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise ToolExecutionError(f"Tool '{name}' execution failed: {exc}") from exc

    def get_statistics(self) -> dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        # Get access control statistics
        access_stats = self.access_manager.get_statistics()

        # Combine with registry statistics
        return {
            "total_tools": len(self.registered_tools),
            "tool_names": list(self.registered_tools.keys()),
            **access_stats,
        }

    def cleanup(self) -> None:
        """Clean up the registry (for testing purposes)."""
        self.registered_tools.clear()
        self.tool_metadata.clear()
        self.access_manager.agent_tool_access.clear()

    # Delegate access control methods to access_manager

    def assign_tools_to_agent(self, agent_id: str, tool_names: list[str]) -> None:
        """
        Assign specific tools to an agent.

        Args:
            agent_id: Unique identifier for the agent
            tool_names: List of tool names to assign
        """
        # Get ALL available tools (local + MCP)
        available_tools = self.get_available_tools()
        self.access_manager.assign_tools(agent_id, tool_names, available_tools)

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """
        Get tools assigned to a specific agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of tool names assigned to the agent
        """
        return self.access_manager.get_agent_tools(agent_id)

    def can_agent_access_tool(self, agent_id: str, tool_name: str) -> bool:
        """
        Check if an agent can access a specific tool.

        Args:
            agent_id: Unique identifier for the agent
            tool_name: Name of the tool to check

        Returns:
            True if agent can access the tool, False otherwise
        """
        return self.access_manager.can_access(agent_id, tool_name)

    def get_agent_tool_metadata(self, agent_id: str) -> list[ToolMetadata]:
        """
        Get tool metadata for tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of ToolMetadata for tools assigned to the agent
        """
        return self.access_manager.get_agent_tool_metadata(agent_id, self.tool_metadata)

    def clear_agent_tools(self, agent_id: str) -> None:
        """
        Clear all tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        self.access_manager.clear_agent_tools(agent_id)

    # Delegate MCP server methods to mcp_manager

    @property
    def mcp_server(self) -> FastMCP | None:
        """
        Get the MCP server instance.

        Returns:
            FastMCP server instance or None if not initialized/available
        """
        return self.mcp_manager.get_server()

    @property
    def agent_tool_access(self) -> dict[str, list[str]]:
        """Expose agent-tool assignments (legacy API expectation)."""
        return self.access_manager.agent_tool_access


# Global registry instance
_registry = ToolRegistry()


# Module-level convenience functions


def get_available_tools() -> list[str]:
    """Get list of available tool names."""
    return _registry.get_available_tools()


def get_mcp_server() -> FastMCP | None:
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
    """Run the MCP server for tool distribution."""
    _registry.mcp_manager.start_server()


def unregister_tool(name: str) -> bool:
    """Unregister a tool from the registry.

    Args:
        name: Tool name to unregister

    Returns:
        True if tool was found and unregistered, False otherwise
    """
    return _registry.unregister_tool(name)
