"""Core Tools Module - Tool registry and management for Phase 2.5.

This module provides:
- ToolRegistry: Singleton for managing tools and FastMCP server
- @tool decorator: For registering user functions as tools
- Tool metadata management
- MCP server integration for tool execution
"""

import sys
from .registry import ToolRegistry, get_available_tools, get_mcp_server, get_tool_metadata, get_tool_registry, run_resources
from .decorator import tool
from .exceptions import (
    ToolError,
    ToolRegistrationError,
    ToolNameConflictError,
    ToolValidationError,
    ToolExecutionError,
    ToolAccessDeniedError,
    ToolNotFoundError
)

__all__ = [
    # Core functionality
    "ToolRegistry",
    "tool",
    "get_available_tools",
    "get_mcp_server",
    "get_tool_metadata",
    "get_tool_registry",
    "run_resources",
    
    # Exceptions
    "ToolError",
    "ToolRegistrationError",
    "ToolNameConflictError",
    "ToolValidationError",
    "ToolExecutionError",
    "ToolAccessDeniedError",
    "ToolNotFoundError",
]
