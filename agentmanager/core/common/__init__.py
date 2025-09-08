"""Common utilities and types for the agent management system."""

from .result import (
    Result, Error, ErrorType,
    validation_error, agent_not_found_error, execution_error, 
    tool_error, timeout_error, permission_error
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