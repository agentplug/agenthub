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

# Import from tools package
from .tools import (
    ToolMetadata,
    ToolRegistry,
    tool,
    register_tool,
    get_global_registry,
    get_tool_metadata,
    ToolRegistrationManager,
    ToolRegistrationError,
    ToolRegistrationResult,
    get_registered_tools_global,
    register_function,
    SecurityLevel,
    SecurityResult,
    ToolExecutionContext,
    ToolSecurityValidator,
    SecureToolExecutor,
    ToolExecutionMonitor,
    SecurityError,
    ToolServiceHost,
    ServiceConfiguration,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolInfoResponse,
    ToolListResponse,
    start_tool_service,
    stop_tool_service,
    get_global_service_host,
    is_service_running,
    ToolValidationConfig,
    ToolValidationResult,
    SignatureValidationResult,
    ToolValidator)

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
    "ToolMetadata",
    "ToolRegistry",
    "tool",
    "register_tool",
    "get_global_registry",
    "get_tool_metadata",
    "ToolRegistrationManager",
    "ToolRegistrationError",
    "ToolRegistrationResult",
    "get_registered_tools_global",
    "register_function",
    "SecurityLevel",
    "SecurityResult",
    "ToolExecutionContext",
    "ToolSecurityValidator",
    "SecureToolExecutor",
    "ToolExecutionMonitor",
    "SecurityError",
    "ToolServiceHost",
    "ServiceConfiguration",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "ToolInfoResponse",
    "ToolListResponse",
    "start_tool_service",
    "stop_tool_service",
    "get_global_service_host",
    "is_service_running",
    "ToolValidationConfig",
    "ToolValidationResult",
    "SignatureValidationResult",
    "ToolValidator",

]
