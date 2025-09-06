"""Core Module - Modular architecture for agent management.

This module provides a modular architecture organized into:
- agents/: Agent lifecycle management, loading, and execution
- runtime/: Runtime management and component coordination
- common/: Shared utilities, types, and exceptions
"""

# Import from agents package
from .agents import (
    AgentLoader, AgentLoadError, AgentWrapper, AgentExecutionError,
    InterfaceValidator, InterfaceValidationError, ManifestParser, ManifestValidationError
)

# Import from tools package
from .tools import (
    ToolRegistry, tool, get_available_tools, get_mcp_server,
    ToolError, ToolRegistrationError, ToolNameConflictError, ToolValidationError,
    ToolExecutionError, ToolAccessDeniedError, ToolNotFoundError
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
]