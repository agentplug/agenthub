"""
Solve Result for Phase 3.2 Intelligent Solve Method

Standardized result format for the solve() method.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SolveResult:
    """
    Standardized result format for the solve() method.

    Provides consistent structure for results from both custom agent
    solve() methods and framework-level method selection.
    """

    # Core result data
    result: Any
    success: bool

    # Method information
    method_used: str | None = None
    method_type: str = "framework"  # "framework" or "custom"

    # Confidence and reasoning
    confidence: float = 1.0
    reasoning: str | None = None

    # Execution metadata
    execution_time: float | None = None
    parameters_used: dict[str, Any] | None = None

    # Error information
    error: str | None = None
    error_type: str | None = None

    # Additional metadata
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "result": self.result,
            "success": self.success,
            "method_used": self.method_used,
            "method_type": self.method_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "execution_time": self.execution_time,
            "parameters_used": self.parameters_used,
            "error": self.error,
            "error_type": self.error_type,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SolveResult":
        """Create SolveResult from dictionary."""
        return cls(
            result=data.get("result"),
            success=data.get("success", False),
            method_used=data.get("method_used"),
            method_type=data.get("method_type", "framework"),
            confidence=data.get("confidence", 1.0),
            reasoning=data.get("reasoning"),
            execution_time=data.get("execution_time"),
            parameters_used=data.get("parameters_used"),
            error=data.get("error"),
            error_type=data.get("error_type"),
            metadata=data.get("metadata"),
        )

    def is_successful(self) -> bool:
        """Check if the solve operation was successful."""
        return self.success and self.error is None

    def has_error(self) -> bool:
        """Check if there was an error."""
        return not self.success or self.error is not None

    def get_error_message(self) -> str:
        """Get error message if available."""
        return self.error or "Unknown error occurred"

    def get_summary(self) -> str:
        """Get a summary of the result."""
        if self.is_successful():
            return (
                f"Successfully solved using {self.method_type} method "
                f"'{self.method_used}'"
            )
        else:
            return f"Failed to solve: {self.get_error_message()}"
