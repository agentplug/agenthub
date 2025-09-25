"""Setup dependency injection container with default services."""

from ..interfaces import (
    KnowledgeManagerProtocol,
    LLMServiceProtocol,
    ToolRegistryProtocol,
)
from .container import get_container
from .providers import (
    KnowledgeManagerProvider,
    LLMServiceProvider,
    ToolRegistryProvider,
)


def setup_di_container() -> None:
    """Setup the DI container with default service providers."""
    container = get_container()

    # Register service providers
    container.register_factory(ToolRegistryProtocol, ToolRegistryProvider.create)  # type: ignore[type-abstract]
    container.register_factory(LLMServiceProtocol, LLMServiceProvider.create)  # type: ignore[type-abstract]
    container.register_factory(
        KnowledgeManagerProtocol, KnowledgeManagerProvider.create  # type: ignore[type-abstract]
    )


def setup_di_container_for_testing() -> None:
    """Setup the DI container with mock services for testing."""
    container = get_container()

    # Clear existing services
    container._services.clear()
    container._factories.clear()

    # Register mock services
    from unittest.mock import Mock

    mock_tool_registry = Mock(spec=ToolRegistryProtocol)
    mock_llm_service = Mock(spec=LLMServiceProtocol)
    mock_knowledge_manager = Mock(spec=KnowledgeManagerProtocol)

    container.register_singleton(ToolRegistryProtocol, mock_tool_registry)  # type: ignore[type-abstract]
    container.register_singleton(LLMServiceProtocol, mock_llm_service)  # type: ignore[type-abstract]
    container.register_singleton(KnowledgeManagerProtocol, mock_knowledge_manager)  # type: ignore[type-abstract]
