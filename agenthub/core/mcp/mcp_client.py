"""MCP Client - Handles MCP client connections and tool execution.

This module provides utilities for connecting to MCP servers and executing tools.
"""

import asyncio
import json
import logging
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from agenthub.core.tools import get_tool_registry

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for tool execution."""

    def __init__(self) -> None:
        """Initialize the MCP client."""
        self.tool_registry = get_tool_registry()
        self.client: ClientSession | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> ClientSession:
        """Connect to the MCP server.

        Returns:
            Connected MCP client session
        """
        async with self._lock:
            if self.client is None:
                # Create connection to our FastMCP server
                server_params = StdioServerParameters(
                    command="python",
                    args=[
                        "-c",
                        "from agenthub.core.tools import get_mcp_server; "
                        "import asyncio; "
                        "asyncio.run(get_mcp_server().run_stdio())",
                    ],
                )

                stdio_transport = stdio_client(server_params)
                self.client = await stdio_transport.__aenter__()

            return self.client

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool through the MCP client.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            JSON string result from tool execution
        """
        from .connection_manager import get_connection_pool

        try:
            async with get_connection_pool().get_connection() as client:
                result = await client.call_tool(tool_name, arguments)

                if result and hasattr(result, "content") and len(result.content) > 0:
                    return (
                        result.content[0].text
                        if hasattr(result.content[0], "text")
                        else str(result.content[0])
                    )
                else:
                    return json.dumps({"error": "No result returned from tool"})

        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return json.dumps(
                {
                    "error": f"Tool execution failed: {str(e)}",
                    "tool_name": tool_name,
                    "error_type": type(e).__name__,
                }
            )

    async def list_tools(self) -> list[str]:
        """List available tools from the MCP server.

        Returns:
            List of available tool names
        """
        return self.tool_registry.get_available_tools()

    async def close(self) -> None:
        """Close the MCP client connection."""
        if self.client:
            if hasattr(self.client, "close"):
                await self.client.close()
            elif hasattr(self.client, "aclose"):
                await self.client.aclose()
            self.client = None


# Global instance
_mcp_client: MCPClient | None = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
