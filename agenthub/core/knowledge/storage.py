"""Knowledge storage for agents."""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class KnowledgeStorage:
    """Stores and retrieves knowledge for agents."""

    def __init__(self, storage_path: Path | None = None):
        """Initialize knowledge storage."""
        self.storage_path = storage_path or Path.home() / ".agenthub" / "knowledge"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def store_knowledge(self, knowledge_text: str, metadata: dict[str, Any]) -> str:
        """Store knowledge with metadata."""
        knowledge_id = self._generate_knowledge_id()

        knowledge_data = {
            "id": knowledge_id,
            "content": knowledge_text,
            "metadata": {
                **metadata,
                "timestamp": time.time(),
                "length": len(knowledge_text),
            },
        }

        knowledge_file = self.storage_path / f"{knowledge_id}.json"

        try:
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(knowledge_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Stored knowledge with ID: {knowledge_id}")
            return knowledge_id

        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            raise

    def retrieve_knowledge(self, knowledge_id: str) -> dict[str, Any] | None:
        """Retrieve knowledge by ID."""
        knowledge_file = self.storage_path / f"{knowledge_id}.json"

        if not knowledge_file.exists():
            return None

        try:
            with open(knowledge_file, encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else None
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge {knowledge_id}: {e}")
            return None

    def list_knowledge(self) -> list[dict[str, Any]]:
        """List all stored knowledge."""
        knowledge_list = []

        for knowledge_file in self.storage_path.glob("*.json"):
            try:
                with open(knowledge_file, encoding="utf-8") as f:
                    knowledge_data = json.load(f)
                    knowledge_list.append(
                        {
                            "id": knowledge_data.get("id"),
                            "metadata": knowledge_data.get("metadata", {}),
                            "file": str(knowledge_file),
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to read knowledge file {knowledge_file}: {e}")

        return knowledge_list

    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete knowledge by ID."""
        knowledge_file = self.storage_path / f"{knowledge_id}.json"

        if not knowledge_file.exists():
            return False

        try:
            knowledge_file.unlink()
            logger.debug(f"Deleted knowledge with ID: {knowledge_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge {knowledge_id}: {e}")
            return False

    def clear_all_knowledge(self) -> int:
        """Clear all stored knowledge."""
        deleted_count = 0

        for knowledge_file in self.storage_path.glob("*.json"):
            try:
                knowledge_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete knowledge file {knowledge_file}: {e}")

        logger.info(f"Cleared {deleted_count} knowledge entries")
        return deleted_count

    def _generate_knowledge_id(self) -> str:
        """Generate unique knowledge ID."""
        import uuid

        return str(uuid.uuid4())

    def get_storage_info(self) -> dict[str, Any]:
        """Get storage information."""
        knowledge_files = list(self.storage_path.glob("*.json"))
        total_size = sum(f.stat().st_size for f in knowledge_files)

        return {
            "storage_path": str(self.storage_path),
            "total_entries": len(knowledge_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
