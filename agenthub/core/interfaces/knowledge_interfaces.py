"""Knowledge-related interfaces to break circular dependencies."""

from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class KnowledgeManagerProtocol(Protocol):
    """Protocol for knowledge manager."""

    def inject_knowledge(
        self, knowledge_text: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """Inject knowledge."""
        ...

    def get_knowledge(self) -> str:
        """Get injected knowledge."""
        ...

    def get_knowledge_metadata(self) -> dict[str, Any]:
        """Get knowledge metadata."""
        ...

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata (alias for get_knowledge_metadata)."""
        ...

    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available."""
        ...

    def clear_knowledge(self) -> None:
        """Clear injected knowledge."""
        ...

    def search_knowledge(self, query: str) -> str | None:
        """Search knowledge."""
        ...

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get knowledge summary."""
        ...
