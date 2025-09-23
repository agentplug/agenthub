"""Unified exception system for AgentHub."""

from typing import Any


class AgentHubError(Exception):
    """Base exception for all AgentHub errors."""

    def __init__(
        self,
        message: str,
        suggestions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.suggestions = suggestions or []
        self.context = context or {}

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.suggestions:
            suggestions_text = "\n".join(
                f"  • {suggestion}" for suggestion in self.suggestions
            )
            return f"{base_msg}\n\nSuggestions:\n{suggestions_text}"
        return base_msg


# Tool-related exceptions
class ToolError(AgentHubError):
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


class ToolConflictError(ToolError):
    """Conflict between built-in and external tools."""

    def __init__(self, message: str, tool_name: str = "", conflict_type: str = ""):
        super().__init__(message)
        self.tool_name = tool_name
        self.conflict_type = conflict_type


# Agent-related exceptions
class AgentError(AgentHubError):
    """Base exception for agent-related errors."""

    pass


class AgentLoadError(AgentError):
    """Raised when agent loading fails."""

    def __init__(
        self,
        message: str,
        agent_name: str = "",
        suggestions: list[str] | None = None,
    ):
        super().__init__(message, suggestions)
        self.agent_name = agent_name

    def __str__(self) -> str:
        message = str(self.args[0]) if self.args else ""
        base_message = (
            f"Failed to load agent '{self.agent_name}': {message}"
            if self.agent_name
            else message
        )
        if self.suggestions:
            suggestions_text = "\n".join(
                f"  • {suggestion}" for suggestion in self.suggestions
            )
            return f"{base_message}\n\nSuggestions:\n{suggestions_text}"
        return base_message


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""

    def __init__(
        self,
        message: str,
        method_name: str = "",
        parameters: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.method_name = method_name
        self.parameters = parameters or {}


# Validation exceptions
class ValidationError(AgentHubError):
    """Raised when parameter validation fails."""

    def __init__(
        self,
        message: str,
        parameter_name: str = "",
        expected_type: str = "",
        actual_value: Any = None,
    ):
        super().__init__(message)
        self.parameter_name = parameter_name
        self.expected_type = expected_type
        self.actual_value = actual_value

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.parameter_name and self.expected_type:
            return (
                f"Validation failed for parameter '{self.parameter_name}': "
                f"expected {self.expected_type}, got {type(self.actual_value).__name__}"
            )
        return base_msg


# Installation exceptions
class InstallationError(AgentHubError):
    """Raised when installation commands fail."""

    def __init__(self, message: str, command: str = "", exit_code: int = 0):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.command:
            return f"Installation failed for command '{self.command}': {base_msg}"
        return base_msg


# Knowledge exceptions
class KnowledgeError(AgentHubError):
    """Raised when knowledge management operations fail."""

    def __init__(self, message: str, operation: str = ""):
        super().__init__(message)
        self.operation = operation


# Configuration exceptions
class ConfigurationError(AgentHubError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_file: str = "", field: str = ""):
        super().__init__(message)
        self.config_file = config_file
        self.field = field
