"""Result type for standardized error handling."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class ErrorType(Enum):
    """Standard error types for the framework."""

    VALIDATION_ERROR = "validation_error"
    AGENT_NOT_FOUND = "agent_not_found"
    EXECUTION_ERROR = "execution_error"
    TOOL_ERROR = "tool_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class Error:
    """Standardized error representation."""

    type: ErrorType
    message: str
    details: dict | None = None
    cause: Exception | None = None

    def to_dict(self) -> dict:
        """Convert error to dictionary."""
        return {
            "type": self.type.value,
            "message": self.message,
            "details": self.details or {},
            "cause": str(self.cause) if self.cause else None,
        }


@dataclass
class Result(Generic[T]):
    """Result type that encapsulates success/failure states."""

    success: bool
    value: T | None = None
    error: Error | None = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """Create a successful result."""
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: Error) -> "Result[T]":
        """Create a failed result."""
        return cls(success=False, error=error)

    @classmethod
    def fail_with(
        cls,
        error_type: ErrorType,
        message: str,
        details: dict | None = None,
        cause: Exception | None = None,
    ) -> "Result[T]":
        """Create a failed result with error details."""
        error = Error(type=error_type, message=message, details=details, cause=cause)
        return cls(success=False, error=error)

    def is_ok(self) -> bool:
        """Check if result is successful."""
        return self.success

    def is_err(self) -> bool:
        """Check if result is an error."""
        return not self.success

    def unwrap(self) -> T:
        """Get the value, raising an exception if result is an error."""
        if self.is_err():
            error_msg = self.error.message if self.error else "Unknown error"
            raise RuntimeError(f"Called unwrap() on error result: {error_msg}")
        if self.value is None:
            raise RuntimeError("Called unwrap() on result with None value")
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the value or return a default if result is an error."""
        if self.is_ok() and self.value is not None:
            return self.value
        return default

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        if self.is_ok():
            return {"success": True, "value": self.value}
        else:
            return {
                "success": False,
                "error": self.error.to_dict() if self.error else None,
            }


# Helper functions for common error types
def validation_error(message: str, details: dict | None = None) -> Error:
    """Create a validation error."""
    return Error(ErrorType.VALIDATION_ERROR, message, details)


def agent_not_found_error(agent_name: str, details: dict | None = None) -> Error:
    """Create an agent not found error."""
    return Error(ErrorType.AGENT_NOT_FOUND, f"Agent not found: {agent_name}", details)


def execution_error(
    message: str, details: dict | None = None, cause: Exception | None = None
) -> Error:
    """Create an execution error."""
    return Error(ErrorType.EXECUTION_ERROR, message, details, cause)


def tool_error(
    message: str, details: dict | None = None, cause: Exception | None = None
) -> Error:
    """Create a tool error."""
    return Error(ErrorType.TOOL_ERROR, message, details, cause)


def timeout_error(timeout: int, details: dict | None = None) -> Error:
    """Create a timeout error."""
    return Error(
        ErrorType.TIMEOUT_ERROR, f"Operation timed out after {timeout} seconds", details
    )


def permission_error(message: str, details: dict | None = None) -> Error:
    """Create a permission error."""
    return Error(ErrorType.PERMISSION_ERROR, message, details)
