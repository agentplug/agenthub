"""MCP Module - Model Context Protocol integration for tool management.

This module provides:
- AgentToolManager: Manages tool assignment and execution for agents
- MCPClient: Handles MCP client connections
- ToolInjector: Injects tool metadata into agent contexts
"""

from .agent_tool_manager import AgentToolManager, get_tool_manager
from .mcp_client import MCPClient, get_mcp_client
from .tool_injector import ToolInjector, get_tool_injector

__all__ = [
    # Main classes
    "AgentToolManager",
    "MCPClient",
    "ToolInjector",
    # Global instances
    "get_tool_manager",
    "get_mcp_client",
    "get_tool_injector",
]
