"""Tool-related exceptions for Phase 2.5."""


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolRegistrationError(ToolError):
    """Tool registration failed."""

    pass


class ToolNameConflictError(ToolError):
    """Tool name already exists."""

    pass


class ToolValidationError(ToolError):
    """Tool validation failed."""

    pass


class ToolExecutionError(ToolError):
    """Tool execution failed."""

    pass


class ToolAccessDeniedError(ToolError):
    """Agent not authorized to access tool."""

    pass


class ToolNotFoundError(ToolError):
    """Tool not found."""

    pass
