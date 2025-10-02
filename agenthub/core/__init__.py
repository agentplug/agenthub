"""Core Module - Modular architecture for agent management.

This module provides a modular architecture organized into:
- agents/: Agent lifecycle management, loading, and execution
- runtime/: Runtime management and component coordination
- common/: Shared utilities, types, and exceptions
- interfaces/: Protocol definitions to break circular dependencies
- di/: Dependency injection container
"""

# Import from agents package
from .agents import (
    AgentInfo,
    AgentLoader,
    AgentWrapper,
    InterfaceValidationError,
    InterfaceValidator,
    ManifestParser,
    ManifestValidationError,
    MethodExecutor,
)

# Import interfaces
from .interfaces import (
    AgentInfoProtocol,
    AgentWrapperProtocol,
    KnowledgeManagerProtocol,
    LLMServiceProtocol,
    MethodExecutorProtocol,
    SolveEngineProtocol,
    ToolManagerProtocol,
    ToolRegistryProtocol,
)

# Import from llm package
from .llm import CoreLLMService

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
from .tools.exceptions import (
    AgentExecutionError,
    AgentHubError,
    AgentLoadError,
    ConfigurationError,
    InstallationError,
    KnowledgeError,
    ToolConflictError,
    ValidationError,
)

__all__ = [
    # Agent components
    "AgentInfo",
    "AgentLoader",
    "AgentLoadError",
    "AgentWrapper",
    "AgentExecutionError",
    "InterfaceValidator",
    "InterfaceValidationError",
    "ManifestParser",
    "ManifestValidationError",
    "MethodExecutor",
    # Interfaces
    "AgentInfoProtocol",
    "AgentWrapperProtocol",
    "KnowledgeManagerProtocol",
    "LLMServiceProtocol",
    "MethodExecutorProtocol",
    "SolveEngineProtocol",
    "ToolManagerProtocol",
    "ToolRegistryProtocol",
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
    # LLM components (new)
    "CoreLLMService",
    # Unified exceptions
    "AgentHubError",
    "ValidationError",
    "ToolConflictError",
    "InstallationError",
    "KnowledgeError",
    "ConfigurationError",
]
