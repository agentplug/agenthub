"""
RAG (Retrieval-Augmented Generation) Builtin Tool Module

Provides document retrieval capabilities with vector search, intelligent ranking,
and support for multiple document formats (PDF, DOCX, MD, TXT, CSV, JSON, etc.).
Features:
- Multi-format document processing
- Local or cloud embeddings (HuggingFace or OpenAI)
- Intelligent LLM-based reranking for better results
- Persistent vector storage with caching
- Query rewriting for improved retrieval
- Clean architecture with dependency injection
- Optimized batch embedding processing

Usage:
    from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig

    # Basic usage with factory function
    rag = create_rag_tool()
    results = rag.search_documents("machine learning concepts")

    # Advanced usage with custom configuration
    config = RAGConfig(
        source_directory="./my-docs",
        embedding_model="google/embeddinggemma-300m",
        default_max_results=10
    )
    rag = create_rag_tool(config=config)
    results = rag.search_documents("neural networks")

"""

import logging
import warnings

from . import compat as _compat  # noqa: F401  ensure llama-index patches are applied
from .config import RAGConfig
from .core import RAGTool
from .document_store import DocumentStore
from .embeddings import EmbeddingService
from .vector_index import VectorIndexManager

logger = logging.getLogger(__name__)

__all__ = [
    "RAGTool",
    "RAGConfig",
    "EmbeddingService",
    "DocumentStore",
    "VectorIndexManager",
    "create_rag_tool",  # Factory function
]


# Legacy singleton instance (deprecated)
_rag_instance = None


def create_rag_tool(config: RAGConfig | None = None) -> RAGTool:
    """
    Factory function to create a RAG tool instance with proper dependency injection.

    This replaces the singleton pattern with explicit instance management and
    provides proper dependency injection for all components.

    Args:
        config: RAG configuration (optional, uses defaults if not provided)

    Returns:
        Configured RAGTool instance

    Example:
        # Basic usage
        rag = create_rag_tool()

        # With custom config
        config = RAGConfig(source_directory="./my-docs")
        rag = create_rag_tool(config=config)
    """
    from agenthub.core.llm.llm_service import get_shared_llm_service

    # Use provided config or create default
    config = config or RAGConfig()

    # Get shared LLM service (integrates with AgentHub)
    llm_service = get_shared_llm_service()

    # Create embedding service
    embedding_service = EmbeddingService(
        model_name=config.embedding_model,
        device=config.embedding_device,
        batch_size=config.embedding_batch_size,
        use_local_embeddings=config.use_local_embeddings,
    )

    # Create document store
    document_store = DocumentStore(
        source_dir=config.source_directory,
        cache_path=config.cached_docs_path,
        supported_extensions=config.supported_extensions,
    )

    # Create vector index manager
    vector_index_manager = VectorIndexManager(storage_dir=config.index_storage_location)

    # Create and return RAG tool with dependency injection
    return RAGTool(
        config=config,
        llm_service=llm_service,
        embedding_service=embedding_service,
        document_store=document_store,
        vector_index_manager=vector_index_manager,
    )


def get_rag_tool() -> RAGTool:
    """
    Get or create a singleton RAG tool instance (DEPRECATED).

    .. deprecated:: 1.0
        Use create_rag_tool() instead for explicit dependency management.

    Returns:
        RAGTool instance
    """
    warnings.warn(
        "get_rag_tool() is deprecated, use create_rag_tool() instead "
        "for explicit dependency management",
        DeprecationWarning,
        stacklevel=2,
    )
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = create_rag_tool()
    return _rag_instance
