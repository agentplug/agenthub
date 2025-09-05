"""MCP (Model Context Protocol) integration for AgentHub.

This module provides a clean abstraction layer over the official MCP Python SDK
for tool communication between agents and tools. Users should import from here
rather than directly from the MCP SDK.
"""

# Re-export the main classes users need
from .server import MCPServer, MCPToolRegistry
from .client import MCPClient, MCPClientManager

# Re-export essential MCP types for advanced users
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

__all__ = [
    # Main AgentHub MCP classes (recommended for users)
    "MCPServer",
    "MCPToolRegistry", 
    "MCPClient",
    "MCPClientManager",
    
    # Advanced MCP SDK classes (for power users)
    "FastMCP",
    "ClientSession",
    "StdioServerParameters", 
    "stdio_client",
]