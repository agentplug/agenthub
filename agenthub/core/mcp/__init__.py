"""MCP Module - Model Context Protocol integration for tool management.

This module provides:
- AgentToolManager: Manages tool assignment and execution for agents
"""

from .agent_tool_manager import AgentToolManager, get_tool_manager

__all__ = [
    "AgentToolManager",
    "get_tool_manager",
]
