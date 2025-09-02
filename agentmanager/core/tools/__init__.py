"""Tools package - Tool registration, validation, security, and execution.

This package contains components for:
- Tool decorator system and metadata
- Tool registration and management
- Tool security validation and sandboxing
- HTTP service hosting for tools
- Tool validation and compliance checking
- Tool execution engine and monitoring
"""

from .decorators import (
    ToolMetadata, ToolRegistry, tool, register_tool,
    get_global_registry, get_tool_metadata, is_tool, _extract_function_metadata
)
from .registry import (
    ToolRegistrationManager, ToolRegistrationError,
    ToolRegistrationResult, get_registered_tools_global,
    register_function, register_tools, is_tool_registered_global,
    get_tool_function_global, get_global_registration_manager
)
from .security import (
    SecurityLevel, SecurityResult, ToolExecutionContext,
    ToolSecurityValidator, SecureToolExecutor, ToolExecutionMonitor,
    SecurityError
)
from .service import (
    ToolServiceHost, ServiceConfiguration, ToolExecutionRequest,
    ToolExecutionResponse, ToolInfoResponse, ToolListResponse,
    start_tool_service, stop_tool_service, get_global_service_host, is_service_running
)
from .validation import (
    ToolValidationConfig, ToolValidationResult, SignatureValidationResult,
    ToolValidator, validate_tool, execute_tool_safely, get_security_report, get_global_validator
)

__all__ = [
    # Decorators
    "ToolMetadata",
    "ToolRegistry",
    "tool",
    "register_tool",
    "get_global_registry",
    "get_tool_metadata",
    "is_tool",
    "_extract_function_metadata",

    # Registry
    "ToolRegistrationManager",
    "ToolRegistrationError",
    "ToolRegistrationResult",
    "get_registered_tools_global",
    "register_function",
    "register_tools",
    "is_tool_registered_global",
    "get_tool_function_global",
    "get_global_registration_manager",

    # Security
    "SecurityLevel",
    "SecurityResult",
    "ToolExecutionContext",
    "ToolSecurityValidator",
    "SecureToolExecutor",
    "ToolExecutionMonitor",
    "SecurityError",

    # Service
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

    # Validation
    "ToolValidationConfig",
    "ToolValidationResult",
    "SignatureValidationResult",
    "ToolValidator",
    "validate_tool",
    "execute_tool_safely",
    "get_security_report",
    "get_global_validator",
]
