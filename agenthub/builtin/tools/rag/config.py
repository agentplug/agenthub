"""
RAG Tool Configuration

Configuration settings for the RAG (Retrieval-Augmented Generation) built-in tool.
Uses Pydantic for validation and type safety.
"""

import copy
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator, validator

# Constants
EMBEDDING_DIMENSION_DEFAULT = 768  # For EmbeddingGemma-300m
EMBEDDING_FALLBACK_VECTOR = [0.0] * EMBEDDING_DIMENSION_DEFAULT
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".md",
    ".csv",
    ".json",
    ".html",
    ".xml",
    ".pptx",
    ".xlsx",
    ".xls",
    ".doc",
}


logger = logging.getLogger(__name__)


def _sanitize_embedding_model_name(model_name: str) -> str:
    """Sanitize embedding model name for filesystem use."""
    model_lower = model_name.lower()

    # Handle special cases first
    if "openai" in model_lower or "ada-002" in model_lower:
        return "openai_embedding"

    # Replace slashes and special chars with underscores
    sanitized = model_name.replace("/", "_").replace("\\", "_")
    # Remove any other problematic characters
    sanitized = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in sanitized)
    return sanitized


class RAGConfig(BaseModel):
    """Configuration for RAG tool with Pydantic validation."""

    # Paths (using Path type for better type safety)
    source_directory: Path = Field(default=Path("./data"))
    cache_directory: Path | None = Field(
        default=None,
        description=(
            "Override default cache directory. "
            "If not provided, uses ~/.agenthub/rag/<source_dir_name>/cache/"
        ),
    )
    cached_docs_path: Path | None = Field(default=None)
    index_storage_location: Path | None = Field(default=None)

    # Embedding settings
    embedding_model: str = Field(default="google/embeddinggemma-300m")
    use_local_embeddings: bool = Field(default=True)
    embedding_batch_size: int = Field(default=8, ge=1, le=128)
    embedding_device: str = Field(default="cpu")

    # LLM settings (now optional, uses CoreLLMService defaults)
    llm_model: str | None = Field(
        default=None
    )  # None = use CoreLLMService auto-detection
    api_timeout_seconds: int = Field(default=20, ge=1, le=300)

    # Search settings
    default_max_results: int = Field(default=5, ge=1, le=100)
    similarity_top_k: int = Field(default=10, ge=1, le=1000)
    max_result_length: int = Field(default=2000, ge=100, le=10000)

    # Query rewriting and ranking
    enable_query_rewriting: bool = Field(default=True)
    enable_intelligent_ranking: bool = Field(default=True)

    # Reindexing option
    is_reindex: bool = Field(
        default=False,
        description=(
            "If True, delete existing index and document cache, then reload "
            "documents and rebuild index from scratch. "
            "Useful when documents changed or index is corrupted."
        ),
    )

    # Advanced settings
    supported_extensions: set[str] = Field(
        default_factory=lambda: SUPPORTED_EXTENSIONS.copy()
    )
    num_workers: int = Field(default=1, ge=1, le=8)

    class Config:
        """Pydantic model configuration."""

        env_prefix = "RAG_"  # Support environment variable overrides
        validate_assignment = True  # Validate on assignment
        arbitrary_types_allowed = True  # Allow Path objects

    @validator("source_directory", "index_storage_location")
    def validate_directories(cls, v: Path) -> Path:
        """Validate and normalize directory paths."""
        # Convert to absolute path if relative
        if not v.is_absolute():
            v = Path.cwd() / v

        # Ensure directories exist (best-effort). If creation fails, leave path intact
        if not v.exists():
            try:
                v.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.warning(
                    f"Could not create directory {v}: {e}. Continuing with path only."
                )

        return v

    @model_validator(mode="after")
    def set_paths_from_collection(self) -> "RAGConfig":
        """
        Set cache_directory and index_storage_location based on source directory
        and embedding model.
        """
        # Only set if not explicitly provided
        if self.cache_directory is None:
            source_dir = self.source_directory or Path("./data")
            embedding_model = self.embedding_model or "google/embeddinggemma-300m"

            source_name = source_dir.resolve().name
            embedding_slug = _sanitize_embedding_model_name(embedding_model)
            collection_slug = f"{source_name}_{embedding_slug}"

            base_dir = Path.home() / ".agenthub" / "rag" / collection_slug
            cache_dir = base_dir / "cache"

            # Ensure directory exists
            if not cache_dir.exists():
                try:
                    cache_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.warning(
                        f"Could not create cache directory {cache_dir}: {e}. "
                        "Continuing with path only."
                    )

            self.cache_directory = cache_dir

        if self.index_storage_location is None:
            source_dir = self.source_directory or Path("./data")
            embedding_model = self.embedding_model or "google/embeddinggemma-300m"

            source_name = source_dir.resolve().name
            embedding_slug = _sanitize_embedding_model_name(embedding_model)
            collection_slug = f"{source_name}_{embedding_slug}"

            base_dir = Path.home() / ".agenthub" / "rag" / collection_slug
            index_dir = base_dir / "index"

            # Ensure directory exists
            if not index_dir.exists():
                try:
                    index_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.warning(
                        f"Could not create index directory {index_dir}: {e}. "
                        "Continuing with path only."
                    )

            self.index_storage_location = index_dir

        # Set cached_docs_path after cache_directory is set
        if self.cached_docs_path is None:
            # Use the cache_directory that was just set (or already exists)
            cache_dir = self.cache_directory
            if cache_dir:
                self.cached_docs_path = cache_dir / "processed_documents.json"
            else:
                # Fallback if cache_directory is still None (shouldn't happen)
                self.cached_docs_path = (
                    Path.home()
                    / ".agenthub"
                    / "rag"
                    / "default"
                    / "cache"
                    / "processed_documents.json"
                )

        return self

    @validator("cache_directory")
    def validate_cache_directory(cls, v: Path) -> Path:
        """Normalize cache directory path."""
        if v is not None:
            v_path = Path(v)
            return v_path.expanduser() if not v_path.is_absolute() else v_path
        return v

    @validator(
        "embedding_batch_size", "default_max_results", "similarity_top_k", "num_workers"
    )
    def validate_positive_integers(cls, v: int) -> int:
        """Validate that integer fields are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @validator("api_timeout_seconds", "max_result_length")
    def validate_reasonable_ranges(cls, v: int) -> int:
        """Validate that values are within reasonable ranges."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    def get_effective_llm_model(self) -> str:
        """Get the LLM model to use (auto-detect if not set)."""
        return self.llm_model or "auto-detect"

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary (for backward compatibility)."""
        return {
            "source_directory": str(self.source_directory),
            "cache_directory": str(self.cache_directory),
            "cached_docs_path": str(self.cached_docs_path),
            "index_storage_location": str(self.index_storage_location),
            "embedding_model": self.embedding_model,
            "use_local_embeddings": self.use_local_embeddings,
            "embedding_batch_size": self.embedding_batch_size,
            "embedding_device": self.embedding_device,
            "llm_model": self.llm_model,
            "api_timeout_seconds": self.api_timeout_seconds,
            "default_max_results": self.default_max_results,
            "similarity_top_k": self.similarity_top_k,
            "max_result_length": self.max_result_length,
            "enable_query_rewriting": self.enable_query_rewriting,
            "enable_intelligent_ranking": self.enable_intelligent_ranking,
            "is_reindex": self.is_reindex,
            "supported_extensions": list(self.supported_extensions),
            "num_workers": self.num_workers,
        }

    @validator("cached_docs_path")
    def validate_cached_docs_path(cls, v: Path) -> Path:
        """Normalize cached docs path."""
        if v is not None:
            v_path = Path(v)
            return v_path.expanduser() if not v_path.is_absolute() else v_path
        return v

    @validator("index_storage_location")
    def validate_index_storage_location(cls, v: Path) -> Path:
        """Normalize index storage location path."""
        if v is not None:
            v_path = Path(v)
            return v_path.expanduser() if not v_path.is_absolute() else v_path
        return v

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "RAGConfig":
        """Create config from dictionary (for backward compatibility)."""
        # Avoid mutating caller-provided dictionaries
        config_copy = copy.deepcopy(config_dict)

        # Convert string paths to Path objects
        path_fields = [
            "source_directory",
            "cache_directory",
            "cached_docs_path",
            "index_storage_location",
        ]
        for field in path_fields:
            if field in config_copy and isinstance(config_copy[field], str):
                config_copy[field] = Path(config_copy[field])

        return cls(**config_copy)

    def validate(self) -> None:
        """Validate configuration settings (backward compatibility)."""
        # Pydantic automatically validates on model creation/assignment
        # This method is kept for backward compatibility
        pass

    def __str__(self) -> str:
        """String representation of the config."""
        return (
            f"RAGConfig(source='{self.source_directory}', "
            f"embedding='{self.embedding_model}')"
        )

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"RAGConfig(source_directory={self.source_directory}, "
            f"embedding_model={self.embedding_model}, "
            f"llm_model={self.llm_model or 'auto-detect'})"
        )
