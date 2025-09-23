"""Knowledge management for agents."""

import logging
from typing import Any

from .storage import KnowledgeStorage
from .validator import KnowledgeValidator

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """Manages knowledge injection and retrieval for agents."""

    def __init__(self, storage: KnowledgeStorage | None = None):
        """Initialize knowledge manager."""
        self.storage = storage or KnowledgeStorage()
        self.validator = KnowledgeValidator()
        self.knowledge: str = ""
        self.metadata: dict[str, Any] = {}
        self.knowledge_id: str | None = None

    def inject_knowledge(
        self, knowledge_text: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """Inject text-based knowledge into agent context."""
        # Validate knowledge
        validation_result = self.validator.validate_knowledge(knowledge_text)
        if not validation_result.is_valid:
            raise ValueError(
                f"Knowledge validation failed: {'; '.join(validation_result.errors)}"
            )

        # Log warnings if any
        if validation_result.warnings:
            for warning in validation_result.warnings:
                logger.warning(f"Knowledge validation warning: {warning}")

        # Validate metadata
        metadata = metadata or {}
        metadata_validation = self.validator.validate_metadata(metadata)
        if not metadata_validation.is_valid:
            raise ValueError(
                f"Metadata validation failed: {'; '.join(metadata_validation.errors)}"
            )

        # Store knowledge
        self.knowledge = knowledge_text
        self.metadata = metadata

        try:
            self.knowledge_id = self.storage.store_knowledge(knowledge_text, metadata)
            logger.info(f"Injected knowledge with ID: {self.knowledge_id}")
            return self.knowledge_id
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            # Still allow knowledge injection even if storage fails
            self.knowledge_id = None
            return "local"

    def get_knowledge(self) -> str:
        """Get injected knowledge."""
        return self.knowledge

    def get_metadata(self) -> dict[str, Any]:
        """Get knowledge metadata."""
        return self.metadata.copy()

    def get_knowledge_id(self) -> str | None:
        """Get knowledge ID."""
        return self.knowledge_id

    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available."""
        return bool(self.knowledge.strip())

    def clear_knowledge(self) -> None:
        """Clear injected knowledge."""
        self.knowledge = ""
        self.metadata = {}
        self.knowledge_id = None
        logger.info("Cleared knowledge")

    def search_knowledge(self, query: str) -> str | None:
        """Search knowledge for relevant information."""
        if not self.is_knowledge_available():
            return None

        # Simple text search - can be enhanced with semantic search
        query_lower = query.lower()
        knowledge_lower = self.knowledge.lower()

        if query_lower in knowledge_lower:
            return self.knowledge

        # Try partial matches
        query_words = query_lower.split()
        if any(word in knowledge_lower for word in query_words):
            return self.knowledge

        return None

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get summary of current knowledge."""
        return {
            "has_knowledge": self.is_knowledge_available(),
            "knowledge_id": self.knowledge_id,
            "length": len(self.knowledge),
            "metadata": self.metadata,
            "storage_info": self.storage.get_storage_info(),
        }

    def load_knowledge_from_id(self, knowledge_id: str) -> bool:
        """Load knowledge from storage by ID."""
        try:
            knowledge_data = self.storage.retrieve_knowledge(knowledge_id)
            if knowledge_data:
                self.knowledge = knowledge_data.get("content", "")
                self.metadata = knowledge_data.get("metadata", {})
                self.knowledge_id = knowledge_id
                logger.info(f"Loaded knowledge from ID: {knowledge_id}")
                return True
            else:
                logger.warning(f"Knowledge not found for ID: {knowledge_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to load knowledge from ID {knowledge_id}: {e}")
            return False

    def list_available_knowledge(self) -> list[dict[str, Any]]:
        """List all available knowledge in storage."""
        return self.storage.list_knowledge()

    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete knowledge from storage."""
        try:
            success = self.storage.delete_knowledge(knowledge_id)
            if success and self.knowledge_id == knowledge_id:
                self.clear_knowledge()
            return success
        except Exception as e:
            logger.error(f"Failed to delete knowledge {knowledge_id}: {e}")
            return False
