"""Core Module - Modular architecture for agent management.

This module provides a modular architecture organized into:
- agents/: Agent lifecycle management, loading, and execution
- runtime/: Runtime management and component coordination
- common/: Shared utilities, types, and exceptions
"""

# Import from agents package
from .agents import (
    AgentLoader, AgentLoadError, AgentWrapper, AgentExecutionError,
    InterfaceValidator, InterfaceValidationError, ManifestParser, ManifestValidationError
)

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
]