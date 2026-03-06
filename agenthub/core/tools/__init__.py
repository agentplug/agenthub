"""Core Tools Module - Tool registry and management for Phase 2.5.

This module provides:
- ToolRegistry: Singleton for managing tools and FastMCP server
- @tool decorator: For registering user functions as tools
- Tool metadata management
- MCP server integration for tool execution
"""

from .decorator import tool
from .exceptions import (
    ToolAccessDeniedError,
    ToolError,
    ToolExecutionError,
    ToolNameConflictError,
    ToolNotFoundError,
    ToolRegistrationError,
    ToolValidationError,
)
from .mcp_server import MCPServerManager
from .registry import (
    ToolRegistry,
    assign_tools_to_agent,
    can_agent_access_tool,
    get_agent_tool_metadata,
    get_agent_tools,
    get_available_tools,
    get_mcp_server,
    get_tool_function,
    get_tool_metadata,
    get_tool_registry,
    run_resources,
    unregister_tool,
)
from .tool_access import ToolAccessManager

__all__ = [
    # Core functionality
    "ToolRegistry",
    "tool",
    "get_available_tools",
    "get_mcp_server",
    "get_tool_metadata",
    "get_tool_registry",
    "get_tool_function",
    "run_resources",
    "unregister_tool",
    # Specialized managers
    "MCPServerManager",
    "ToolAccessManager",
    # Tool access control
    "assign_tools_to_agent",
    "get_agent_tools",
    "can_agent_access_tool",
    "get_agent_tool_metadata",
    # Exceptions
    "ToolError",
    "ToolRegistrationError",
    "ToolNameConflictError",
    "ToolValidationError",
    "ToolExecutionError",
    "ToolAccessDeniedError",
    "ToolNotFoundError",
]
