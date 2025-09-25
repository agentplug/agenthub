"""Dependency injection container for AgentHub.

This module provides a simple dependency injection container to resolve
circular dependencies and improve testability.
"""

from .container import DIContainer, get_container
from .providers import (
    KnowledgeManagerProvider,
    LLMServiceProvider,
    ToolRegistryProvider,
)

__all__ = [
    "DIContainer",
    "get_container",
    "ToolRegistryProvider",
    "LLMServiceProvider",
    "KnowledgeManagerProvider",
]
