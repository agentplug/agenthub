"""Core Module - Modular architecture for agent management.

This module provides a modular architecture organized into:
- agents/: Agent lifecycle management, loading, and execution
- runtime/: Runtime management and component coordination
- common/: Shared utilities, types, and exceptions
"""

# Import from agents package
from .agents import (
    AgentExecutionError,
    AgentLoader,
    AgentLoadError,
    AgentWrapper,
    InterfaceValidationError,
    InterfaceValidator,
    ManifestParser,
    ManifestValidationError,
)

# Import from mcp package
from .mcp import (
    AgentToolManager,
    MCPClient,
    ToolInjector,
    get_mcp_client,
    get_tool_injector,
    get_tool_manager,
)

# Import from tools package
from .tools import (
    ToolAccessDeniedError,
    ToolError,
    ToolExecutionError,
    ToolNameConflictError,
    ToolNotFoundError,
    ToolRegistrationError,
    ToolRegistry,
    ToolValidationError,
    get_available_tools,
    get_mcp_server,
    tool,
)

__all__ = [
    # Agent components
    "AgentLoader",
    "AgentLoadError",
    "AgentWrapper",
    "AgentExecutionError",
    "InterfaceValidator",
    "InterfaceValidationError",
    "ManifestParser",
    "ManifestValidationError",
    # Tool components
    "ToolRegistry",
    "tool",
    "get_available_tools",
    "get_mcp_server",
    "ToolError",
    "ToolRegistrationError",
    "ToolNameConflictError",
    "ToolValidationError",
    "ToolExecutionError",
    "ToolAccessDeniedError",
    "ToolNotFoundError",
    "run_resources",
    # MCP components (new)
    "AgentToolManager",
    "MCPClient",
    "ToolInjector",
    "get_tool_manager",
    "get_mcp_client",
    "get_tool_injector",
]
