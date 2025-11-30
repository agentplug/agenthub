"""
Embedding Service for RAG Tool

Provides optimized embedding generation with batch processing and UTF-8 encoding fixes.
Supports both local (SentenceTransformer) and OpenAI embeddings.
"""

import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from .config import (
    create_fallback_vector,
    get_model_dimension,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding service with optimized batch processing and UTF-8 encoding fixes.

    This service provides:
    - Custom embedding wrapper for UTF-8 encoding fixes
    - Optimized batch processing (instead of sequential)
    - Model initialization and configuration
    - Error handling and fallback embeddings
    - Async support for future enhancements
    """

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 8,
        cache_dir: Path | None = None,
        use_local_embeddings: bool = False,
    ):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the embedding model to use
            device: Device to run the model on ("cpu" or "cuda") - only for local models
            batch_size: Batch size for processing multiple texts
            cache_dir: Directory to cache the model (only for local models)
                (default: .cache/sentence_transformers)
            use_local_embeddings: Whether to use local SentenceTransformer models
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.use_local_embeddings = use_local_embeddings

        # Set up cache directory for local models
        if cache_dir is None and use_local_embeddings:
            cache_dir = Path.cwd() / ".cache" / "sentence_transformers"

        self.cache_dir = cache_dir
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing embedding service with model: {model_name}")
        logger.info(f"Local embeddings: {use_local_embeddings}")
        if use_local_embeddings:
            logger.info(f"Cache directory: {self.cache_dir}")
            logger.info(f"Device: {device}, Batch size: {batch_size}")

        # Initialize the model
        self._model = self._initialize_model()

        # Initialize OpenAI client if needed
        self._openai_client = None
        if not self.use_local_embeddings:
            self._openai_client = self._initialize_openai_client()

    def _initialize_model(self):
        """Initialize the embedding model (local SentenceTransformer or OpenAI)."""
        if self.use_local_embeddings:
            # Use local SentenceTransformer model
            try:
                model = SentenceTransformer(
                    self.model_name,
                    device=self.device,
                    trust_remote_code=True,
                    cache_folder=str(self.cache_dir),
                )
                logger.info(
                    f"✅ Successfully loaded local embedding model: {self.model_name}"
                )
                return model
            except Exception as e:
                logger.error(
                    f"Failed to load local embedding model {self.model_name}: {e}"
                )
                raise RuntimeError(
                    f"Cannot initialize local embedding model: {e}"
                ) from e
        else:
            # Use OpenAI embeddings - will be handled in encode methods
            logger.info(f"✅ Using OpenAI embeddings: {self.model_name}")
            return None  # No local model needed for OpenAI

    def _initialize_openai_client(self):
        """Initialize OpenAI client for embeddings."""
        if not OPENAI_AVAILABLE:
            raise RuntimeError(
                "OpenAI library not installed. Install with: pip install openai"
            )

        try:
            # Initialize client (will use OPENAI_API_KEY environment variable)
            client = OpenAI()
            logger.info("✅ Successfully initialized OpenAI client")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Cannot initialize OpenAI client: {e}") from e

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for embedding.

        Handles UTF-8 encoding issues and empty text.
        """
        # Handle None or empty text
        if not text or not isinstance(text, str):
            return " "

        # Strip whitespace
        text = text.strip()
        if not text:
            return " "

        # Fix UTF-8 encoding issues efficiently
        try:
            text = text.encode("utf-8", errors="ignore").decode("utf-8")
        except Exception:
            text = " "

        return text

    def encode_text(self, text: str) -> list[float]:
        """
        Get embedding for a single text.

        Args:
            text: Text to encode

        Returns:
            Embedding vector as list of floats
        """
        cleaned_text = self._clean_text(text)

        if self.use_local_embeddings:
            # Use local SentenceTransformer model
            try:
                embedding = self._model.encode(
                    cleaned_text,
                    convert_to_tensor=False,
                    normalize_embeddings=True,
                )
                return embedding.tolist()
            except Exception as e:
                logger.warning(f"Local embedding error for text '{text[:50]}...': {e}")
                # Create model-specific fallback vector
                dimension = get_model_dimension(
                    self.model_name, use_local_embeddings=True
                )
                return create_fallback_vector(self.model_name, dimension)
        else:
            # Use OpenAI embeddings
            try:
                response = self._openai_client.embeddings.create(
                    model=self.model_name, input=cleaned_text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI embedding error for text '{text[:50]}...': {e}")
                # Create model-specific fallback vector
                dimension = get_model_dimension(
                    self.model_name, use_local_embeddings=False
                )
                return create_fallback_vector(self.model_name, dimension)

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts using optimized batch processing.

        This is the main optimization - instead of processing texts sequentially,
        we process them in true batches.

        Args:
            texts: List of texts to encode

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Clean all texts at once
        cleaned_texts = [self._clean_text(text) for text in texts]

        if self.use_local_embeddings:
            # Use local SentenceTransformer model
            try:
                # Single encode call for the entire batch - much faster!
                embeddings = self._model.encode(
                    cleaned_texts,
                    convert_to_tensor=False,
                    normalize_embeddings=True,
                    batch_size=self.batch_size,
                    show_progress_bar=False,  # Disable progress bar for library use
                )

                # Convert to list format
                return [emb.tolist() for emb in embeddings]

            except Exception as e:
                logger.error(f"Local batch embedding error: {e}")
                # Fallback: process individually
                logger.warning("Falling back to individual text processing")
                return [self.encode_text(text) for text in texts]
        else:
            # Use OpenAI embeddings - process individually for now
            # Note: OpenAI has batch limits, so processing individually is safer
            logger.info(f"Processing {len(texts)} texts with OpenAI embeddings")
            return [self.encode_text(text) for text in texts]

    def encode_query(self, query: str) -> list[float]:
        """
        Get embedding for a search query.

        Args:
            query: Search query to encode

        Returns:
            Query embedding vector
        """
        # For now, treat queries the same as regular text
        # In the future, we might add query-specific preprocessing
        return self.encode_text(query)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Dimension of embedding vectors
        """
        # Use model-specific dimension detection
        return get_model_dimension(self.model_name, self.use_local_embeddings)

    def get_model_info(self) -> dict:
        """
        Get information about the embedding model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "batch_size": self.batch_size,
            "use_local_embeddings": self.use_local_embeddings,
            "embedding_type": "local" if self.use_local_embeddings else "openai",
            "embedding_dimension": self.get_embedding_dimension(),
            "cache_dir": str(self.cache_dir) if self.cache_dir else None,
            "openai_available": OPENAI_AVAILABLE,
        }

    def __repr__(self) -> str:
        """String representation of the service."""
        return (
            f"EmbeddingService(model='{self.model_name}', "
            f"device='{self.device}', batch_size={self.batch_size})"
        )
