"""Agents package - Agent lifecycle management, loading, and execution.

This package contains components for:
- Agent discovery and loading
- Agent execution wrapper and interface
- Agent interface validation
- Agent manifest parsing and validation
"""

from ..tools.exceptions import AgentExecutionError
from .execution import DynamicAgentExecutor, DynamicExecutionError, MethodExecutor
from .lifecycle import (
    AgentLoader,
    AgentLoadError,
    InterfaceValidationError,
    InterfaceValidator,
    ManifestParser,
    ManifestValidationError,
)
from .models import AgentInfo
from .orchestration import AgentWrapper
from .solve import AgentSolveInterface, SolveResult

__all__ = [
    "AgentInfo",
    "AgentLoader",
    "AgentLoadError",
    "AgentWrapper",
    "AgentExecutionError",
    "AgentSolveInterface",
    "SolveResult",
    "InterfaceValidator",
    "InterfaceValidationError",
    "ManifestParser",
    "ManifestValidationError",
    "MethodExecutor",
    "DynamicAgentExecutor",
    "DynamicExecutionError",
]
