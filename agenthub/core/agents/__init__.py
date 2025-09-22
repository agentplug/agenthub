"""Agents package - Agent lifecycle management, loading, and execution.

This package contains components for:
- Agent discovery and loading
- Agent execution wrapper and interface
- Agent interface validation
- Agent manifest parsing and validation
"""

from .dynamic_executor import DynamicAgentExecutor, DynamicExecutionError
from .loader import AgentLoader, AgentLoadError
from .manifest import ManifestParser, ManifestValidationError
from .solve_interface import AgentSolveInterface
from .solve_result import SolveResult
from .validator import InterfaceValidationError, InterfaceValidator
from .wrapper import AgentExecutionError, AgentWrapper

__all__ = [
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
    "DynamicAgentExecutor",
    "DynamicExecutionError",
]
