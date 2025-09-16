"""Common utilities and types for the agent management system."""

from .result import (
    Error,
    ErrorType,
    Result,
    agent_not_found_error,
    execution_error,
    permission_error,
    timeout_error,
    tool_error,
    validation_error,
)

__all__ = [
    "Result",
    "Error",
    "ErrorType",
    "validation_error",
    "agent_not_found_error",
    "execution_error",
    "tool_error",
    "timeout_error",
    "permission_error",
]
