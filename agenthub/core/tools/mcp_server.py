"""MCP Server Management Module.

This module handles MCP (Model Context Protocol) server lifecycle,
configuration, and management.
"""

import logging

from mcp.server import FastMCP

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Manages MCP server lifecycle and configuration.

    Responsibilities:
    - Loading MCP configuration from config or environment
    - Creating and initializing FastMCP server instances
    - Starting the MCP server via SSE transport
    """

    def __init__(self) -> None:
        """Initialize the MCP server manager."""
        self.mcp_server: FastMCP | None = None

    def get_config(self) -> tuple[str, int]:
        """
        Get MCP configuration from config or environment variables.

        Returns:
            tuple: (host, port)

        Raises:
            ValueError: If port value is invalid
        """
        # Try to get from config first
        try:
            from agenthub.config import get_config

            config = get_config()
            return config.mcp_host, config.mcp_port
        except (ImportError, AttributeError):
            # Fallback to environment variables if config not available
            import os

            host = os.getenv("AGENTHUB_MCP_HOST", "localhost")
            port_str = os.getenv("AGENTHUB_MCP_PORT", "8000")

            try:
                port = int(port_str)
                if port <= 0 or port > 65535:
                    raise ValueError(f"Invalid port number: {port}")
            except ValueError as e:
                raise ValueError(f"Invalid AGENTHUB_MCP_PORT value: {port_str}") from e

            return host, port

    def create_server(self, host: str, port: int) -> FastMCP | None:
        """
        Create FastMCP server with the given configuration.

        Args:
            host: Host to bind to
            port: Port to bind to

        Returns:
            FastMCP server instance or None if creation fails
        """
        try:
            if host == "localhost" and port == 8000:
                return FastMCP("AgentHub Tools")
            else:
                return FastMCP("AgentHub Tools", host="0.0.0.0", port=port)
        except (ImportError, NameError):
            # MCP library not available
            return None
        except Exception as e:
            # Log the error but don't crash
            logger.warning(f"Failed to create MCP server: {e}")
            return None

    def initialize(self) -> None:
        """Initialize the MCP server with configuration."""
        host, port = self.get_config()
        self.mcp_server = self.create_server(host, port)

    def get_server(self) -> FastMCP | None:
        """
        Get the MCP server instance.

        Returns:
            FastMCP server instance or None if not initialized/available
        """
        if self.mcp_server is None:
            self.initialize()
        return self.mcp_server

    def start_server(self) -> None:
        """Start the MCP server via SSE transport."""
        mcp_server = self.get_server()
        if mcp_server is None:
            raise RuntimeError(
                "MCP server not available. This may be because:\n"
                "  1. The 'mcp' package is not installed (pip install mcp)\n"
                "  2. MCP server initialization failed during startup\n"
                "  3. Invalid MCP configuration"
            )
        mcp_server.run(transport="sse")
