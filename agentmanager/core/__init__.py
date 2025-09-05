"""Core Module - Modular architecture for agent and tool management.

This module provides a modular architecture organized into:
- agents/: Agent lifecycle management, loading, and execution
- tools/: Tool registration, validation, security, and execution
- runtime/: Runtime management and component coordination
- common/: Shared utilities, types, and exceptions
"""

# Import from agents package
from .agents import (
    AgentLoader, AgentLoadError, AgentWrapper, AgentExecutionError,
    InterfaceValidator, InterfaceValidationError, ManifestParser, ManifestValidationError
)

# Import from tools package (Phase 2.5 MCP implementation)
from .tools import (
    tool,
    ToolDiscovery,
    ToolRegistry
)

# Import from MCP package
from .mcp import (
    MCPServer,
    MCPClient,
    MCPToolRegistry,
    MCPClientManager
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

    # Tool components (Phase 2.5 MCP implementation)
    "tool",
    "ToolDiscovery",
    "ToolRegistry",

    # MCP components
    "MCPServer",
    "MCPClient",
    "MCPToolRegistry",
    "MCPClientManager",
]
