"""Core Tools Module - Tool registry and management for Phase 2.5.

This module provides:
- ToolRegistry: Singleton for managing tools and FastMCP server
- @tool decorator: For registering user functions as tools
- Built-in tools: web_search, data_analyzer
- Tool metadata management
"""

from .registry import ToolRegistry, get_available_tools, get_mcp_server
from .decorator import tool
from .builtin_tools import web_search, data_analyzer
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
    
    # Built-in tools
    "web_search",
    "data_analyzer",
    
    # Exceptions
    "ToolError",
    "ToolRegistrationError",
    "ToolNameConflictError",
    "ToolValidationError",
    "ToolExecutionError",
    "ToolAccessDeniedError",
    "ToolNotFoundError",
]
