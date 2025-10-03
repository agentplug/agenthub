"""Core interfaces to break circular dependencies.

This module defines protocols and interfaces that allow components to depend
on abstractions rather than concrete implementations, breaking circular imports.
"""

from .agent_interfaces import (
    AgentInfoProtocol,
    AgentWrapperProtocol,
    MethodExecutorProtocol,
    SolveEngineProtocol,
)
from .knowledge_interfaces import (
    KnowledgeManagerProtocol,
)
from .llm_interfaces import (
    LLMDecisionMakerProtocol,
    LLMServiceProtocol,
)
from .tool_interfaces import (
    ToolExecutionProtocol,
    ToolManagerProtocol,
    ToolRegistryProtocol,
)

__all__ = [
    # Agent interfaces
    "AgentInfoProtocol",
    "AgentWrapperProtocol",
    "MethodExecutorProtocol",
    "SolveEngineProtocol",
    # Tool interfaces
    "ToolRegistryProtocol",
    "ToolManagerProtocol",
    "ToolExecutionProtocol",
    # LLM interfaces
    "LLMServiceProtocol",
    "LLMDecisionMakerProtocol",
    # Knowledge interfaces
    "KnowledgeManagerProtocol",
]
