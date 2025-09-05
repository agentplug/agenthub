"""Tool system for AgentHub with @tool decorator and MCP integration.

This module provides the @tool decorator for users to define tools that can be
automatically discovered and made available to agents via MCP protocol.
"""

from .decorators import (
    tool, register_tool, ToolMetadata, get_tool_metadata, is_tool
)
from .registry import ToolRegistry, get_global_registry
from .discovery import ToolDiscovery

__all__ = [
    "tool",
    "register_tool", 
    "ToolMetadata",
    "ToolRegistry",
    "ToolDiscovery",
    "get_global_registry",
    "get_tool_metadata",
    "is_tool",
]