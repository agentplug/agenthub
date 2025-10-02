"""Service providers for dependency injection."""

from ..interfaces import (
    KnowledgeManagerProtocol,
    LLMServiceProtocol,
    ToolRegistryProtocol,
)


class ToolRegistryProvider:
    """Provider for tool registry."""

    @staticmethod
    def create() -> ToolRegistryProtocol:
        """Create tool registry instance."""
        # Import here to avoid circular dependency
        from ..tools import get_tool_registry

        return get_tool_registry()


class LLMServiceProvider:
    """Provider for LLM service."""

    @staticmethod
    def create() -> LLMServiceProtocol:
        """Create LLM service instance."""
        # Import here to avoid circular dependency
        from ..llm import get_shared_llm_service

        service = get_shared_llm_service()
        # Cast to protocol to satisfy type checker
        return service  # type: ignore[return-value]


class KnowledgeManagerProvider:
    """Provider for knowledge manager."""

    @staticmethod
    def create() -> KnowledgeManagerProtocol:
        """Create knowledge manager instance."""
        # Import here to avoid circular dependency
        from ..knowledge import KnowledgeManager

        manager = KnowledgeManager()
        # Cast to protocol to satisfy type checker
        return manager  # type: ignore[return-value]
