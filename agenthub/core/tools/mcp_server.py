"""MCP Server Management Module.

This module handles MCP (Model Context Protocol) server lifecycle,
configuration, and management.
"""

# Deferred annotation evaluation is required here: FastMCP may be None
# (import fallback below), and evaluated `FastMCP | None` annotations
# would raise TypeError at import time.
from __future__ import annotations

import logging

# FastMCP moved between mcp releases; try both locations, then chuk_mcp.
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server import FastMCP  # type: ignore[attr-defined,no-redef]
    except ImportError:
        try:
            from chuk_mcp.server import MCPServer as FastMCP  # type: ignore
        except ImportError:
            FastMCP = None  # type: ignore[assignment,misc]

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

            # Smart port defaulting based on host
            # Localhost/dev hosts default to 8000 (HTTP)
            # All other hosts default to 443 (HTTPS)
            if host in ["localhost", "127.0.0.1", "0.0.0.0"]:
                default_port = "8000"  # Dev default
            else:
                default_port = "443"  # Prod default (HTTPS)

            port_str = os.getenv("AGENTHUB_MCP_PORT", default_port)

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
