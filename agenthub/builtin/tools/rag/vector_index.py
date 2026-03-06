"""
Vector Index Manager for RAG Tool

Provides vector index lifecycle management including building, loading, and persistence.
"""

import logging
from pathlib import Path

from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

logger = logging.getLogger(__name__)


class VectorIndexManager:
    """
    Vector index manager for building, loading, and persisting vector indices.

    Responsibilities:
    - Build vector indices from documents
    - Load existing indices from storage
    - Persist indices to disk
    - Handle empty document collections
    - Storage context management
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize the vector index manager.

        Args:
            storage_dir: Directory to store vector indices
        """
        self.storage_dir = storage_dir

        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized VectorIndexManager")
        logger.info(f"Storage directory: {self.storage_dir}")

    def build_or_load(
        self, documents: list[Document], force_rebuild: bool = False
    ) -> VectorStoreIndex:
        """
        Build a new vector index or load an existing one.

        Args:
            documents: List of documents to index
            force_rebuild: If True, delete existing index and rebuild from scratch

        Returns:
            VectorStoreIndex instance
        """
        # Handle empty document collection
        if not documents:
            logger.warning("No documents provided. Creating empty vector index.")
            return VectorStoreIndex([])

        # Force rebuild: clear existing index
        if force_rebuild:
            logger.info("Force rebuild requested. Clearing existing index...")
            self.clear_index()

        # Check if a valid index already exists (skip if force_rebuild)
        if not force_rebuild and self._is_index_valid(documents):
            logger.info(f"Loading existing index from storage: {self.storage_dir}")
            return self._load_from_storage()

        # Build new index
        logger.info(f"Creating new vector index with {len(documents)} documents")
        index = self._build_index(documents)

        # Persist the index
        logger.info(f"Persisting index to storage: {self.storage_dir}")
        self._persist(index)

        return index

    def _is_index_valid(self, documents: list[Document]) -> bool:
        """
        Check if an existing index is valid and up-to-date.

        Args:
            documents: List of documents to compare against

        Returns:
            True if existing index is valid
        """
        if not self.index_exists():
            return False

        try:
            # Try to load the existing index
            storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
            existing_index = load_index_from_storage(storage_context)

            # Check if the number of documents matches
            # This is a simple heuristic - in a production system, you might want
            # to check document hashes or modification times
            if hasattr(existing_index, "docstore"):
                doc_count = len(existing_index.docstore.docs)
                if doc_count == len(documents):
                    logger.info(f"Existing index is valid ({doc_count} documents)")
                    return True
                else:
                    logger.info(
                        f"Index document count mismatch: {doc_count} vs "
                        f"{len(documents)}. Rebuilding..."
                    )
                    return False
            else:
                # Can't determine document count, assume index is valid
                logger.info("Cannot determine document count, assuming index is valid")
                return True

        except Exception as e:
            logger.warning(f"Failed to validate existing index: {e}")
            self.clear_index()
            return False

    def _load_from_storage(self) -> VectorStoreIndex:
        """
        Load an existing vector index from storage.

        Returns:
            VectorStoreIndex instance
        """
        try:
            storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
            index = load_index_from_storage(storage_context)
            logger.info("Successfully loaded index from storage")
            return index

        except Exception as e:
            logger.error(f"Failed to load index from storage: {e}")
            self.clear_index()
            logger.warning("Creating empty index as fallback")
            return VectorStoreIndex([])

    def _build_index(self, documents: list[Document]) -> VectorStoreIndex:
        """
        Build a new vector index from documents.

        Args:
            documents: List of documents to index

        Returns:
            VectorStoreIndex instance
        """
        try:
            # Create the index
            index = VectorStoreIndex.from_documents(documents)
            logger.info(f"Successfully built index with {len(documents)} documents")
            return index

        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
            logger.warning("Creating empty index as fallback")
            return VectorStoreIndex([])

    def _persist(self, index: VectorStoreIndex) -> None:
        """
        Persist a vector index to storage.

        Args:
            index: VectorStoreIndex to persist
        """
        try:
            index.storage_context.persist(persist_dir=self.storage_dir)
            logger.info(f"Successfully persisted index to: {self.storage_dir}")

        except (AttributeError, TypeError) as e:
            # Handle graph store serialization issues
            # (e.g., 'SimpleGraphStoreData' object has no attribute 'to_dict')
            error_str = str(e).lower()
            if "to_dict" in error_str or "graph" in error_str:
                logger.warning(f"Graph store persistence issue detected: {e}")
                logger.warning("Attempting to persist core components individually...")
                try:
                    # Persist individual components that are essential for vector search
                    # These don't depend on graph store serialization
                    # Individual persist methods use persist_path (file path)
                    # not persist_dir
                    storage_path = str(self.storage_dir)
                    if hasattr(index.storage_context, "docstore") and hasattr(
                        index.storage_context.docstore, "persist"
                    ):
                        index.storage_context.docstore.persist(
                            persist_path=f"{storage_path}/docstore.json"
                        )
                    if hasattr(index.storage_context, "index_store") and hasattr(
                        index.storage_context.index_store, "persist"
                    ):
                        index.storage_context.index_store.persist(
                            persist_path=f"{storage_path}/index_store.json"
                        )
                    if hasattr(index.storage_context, "vector_store") and hasattr(
                        index.storage_context.vector_store, "persist"
                    ):
                        index.storage_context.vector_store.persist(
                            persist_path=f"{storage_path}/vector_store.json"
                        )
                    logger.info(
                        "Partially persisted index (core components only) "
                        f"to: {self.storage_dir}"
                    )
                except Exception as e2:
                    logger.error(f"Failed to persist index components: {e2}")
                    # Don't fail if persistence fails - the index is still
                    # usable in memory
            else:
                logger.error(f"Failed to persist index: {e}")
                # Don't fail if persistence fails - the index is still usable in memory

        except Exception as e:
            logger.error(f"Failed to persist index: {e}")
            # Don't fail if persistence fails - the index is still usable in memory

    def index_exists(self) -> bool:
        """
        Check if a vector index exists in storage.

        Returns:
            True if index exists
        """
        base_required = ["docstore.json", "index_store.json"]
        for filename in base_required:
            file_path = self.storage_dir / filename
            if not file_path.exists():
                return False

        vector_store_candidates = ["vector_store.json", "default__vector_store.json"]
        if not any(
            (self.storage_dir / name).exists() for name in vector_store_candidates
        ):
            return False

        return True

    def clear_index(self) -> bool:
        """
        Clear the vector index from storage.

        Returns:
            True if index was cleared successfully
        """
        try:
            # Remove all index files
            required_files = [
                "docstore.json",
                "index_store.json",
                "vector_store.json",
                "graph_store.json",
            ]

            for filename in required_files:
                file_path = self.storage_dir / filename
                if file_path.exists():
                    file_path.unlink()

            logger.info(f"Cleared vector index from: {self.storage_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False

    def get_index_stats(self) -> dict:
        """
        Get statistics about the vector index.

        Returns:
            Dictionary with index statistics
        """
        stats = {
            "storage_dir": str(self.storage_dir),
            "index_exists": self.index_exists(),
        }

        if self.index_exists():
            try:
                # Load the index to get stats
                storage_context = StorageContext.from_defaults(
                    persist_dir=self.storage_dir
                )
                index = load_index_from_storage(storage_context)

                # Try to get document count
                if hasattr(index, "docstore") and hasattr(index.docstore, "docs"):
                    stats["document_count"] = len(index.docstore.docs)
                else:
                    stats["document_count"] = "unknown"

                # Add storage info
                total_size = 0
                for filename in [
                    "docstore.json",
                    "index_store.json",
                    "vector_store.json",
                ]:
                    file_path = self.storage_dir / filename
                    if file_path.exists():
                        total_size += file_path.stat().st_size

                stats["storage_size_bytes"] = total_size
                stats["storage_size_mb"] = round(total_size / (1024 * 1024), 2)

            except Exception as e:
                logger.error(f"Failed to get index stats: {e}")
                stats["error"] = str(e)

        return stats

    def __repr__(self) -> str:
        """String representation of the vector index manager."""
        exists = self.index_exists()
        return (
            f"VectorIndexManager(storage_dir='{self.storage_dir}', "
            f"index_exists={exists})"
        )
