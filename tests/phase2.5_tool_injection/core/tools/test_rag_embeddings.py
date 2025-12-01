"""
Tests for RAG Embedding Service
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agenthub.builtin.tools.rag.config import EMBEDDING_DIMENSION_DEFAULT
from agenthub.builtin.tools.rag.embeddings import EmbeddingService


class TestEmbeddingService:
    """Test suite for EmbeddingService."""

    def test_initialization(self):
        """Test service initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            service = EmbeddingService(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu",
                batch_size=4,
                cache_dir=cache_dir,
            )

            assert service.model_name == "sentence-transformers/all-MiniLM-L6-v2"
            assert service.device == "cpu"
            assert service.batch_size == 4
            assert service.cache_dir == cache_dir

    @patch("agenthub.builtin.tools.rag.embeddings.SentenceTransformer")
    def test_model_initialization_failure(self, mock_transformer):
        """Test handling of model initialization failure."""
        mock_transformer.side_effect = Exception("Model not found")

        with pytest.raises(RuntimeError, match="Cannot initialize embedding model"):
            EmbeddingService(model_name="invalid-model")

    def test_clean_text_empty_input(self):
        """Test text cleaning with empty input."""
        service = self._create_mock_service()

        assert service._clean_text("") == " "
        assert service._clean_text("   ") == " "
        assert service._clean_text(None) == " "  # type: ignore
        assert service._clean_text(123) == " "  # type: ignore

    def test_clean_text_utf8_handling(self):
        """Test UTF-8 encoding fixes in text cleaning."""
        service = self._create_mock_service()

        # Test normal text
        text = "Hello, world!"
        cleaned = service._clean_text(text)
        assert cleaned == text

        # Test text with special characters
        text = "Café résumé naïve"
        cleaned = service._clean_text(text)
        assert "caf" in cleaned.lower()  # Should handle accents

    def test_encode_text_single(self):
        """Test single text encoding."""
        service = self._create_mock_service()
        import numpy as np

        mock_embedding = np.array([0.1, 0.2, 0.3, 0.4])

        with patch.object(service._model, "encode", return_value=mock_embedding):
            result = service.encode_text("test text")

            assert result == [0.1, 0.2, 0.3, 0.4]
            service._model.encode.assert_called_once_with(
                "test text", convert_to_tensor=False, normalize_embeddings=True
            )

    def test_encode_text_with_fallback(self):
        """Test encoding with fallback on error."""
        service = self._create_mock_service()

        with patch.object(
            service._model, "encode", side_effect=Exception("Encoding failed")
        ):
            result = service.encode_text("test text")

            # Should return fallback vector
            assert result == [0.0] * EMBEDDING_DIMENSION_DEFAULT

    def test_encode_batch(self):
        """Test batch encoding optimization."""
        service = self._create_mock_service()
        texts = ["text1", "text2", "text3"]
        import numpy as np

        mock_embeddings = [
            np.array([0.1, 0.2]),
            np.array([0.3, 0.4]),
            np.array([0.5, 0.6]),
        ]

        with patch.object(service._model, "encode", return_value=mock_embeddings):
            results = service.encode_batch(texts)

            assert results == [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
            service._model.encode.assert_called_once_with(
                ["text1", "text2", "text3"],
                convert_to_tensor=False,
                normalize_embeddings=True,
                batch_size=service.batch_size,
                show_progress_bar=False,
            )

    def test_encode_batch_empty_list(self):
        """Test batch encoding with empty list."""
        service = self._create_mock_service()

        results = service.encode_batch([])
        assert results == []

    def test_encode_batch_fallback_on_error(self):
        """Test batch encoding fallback to individual processing."""
        service = self._create_mock_service()
        texts = ["text1", "text2"]

        # Mock batch failure
        with patch.object(
            service._model, "encode", side_effect=Exception("Batch failed")
        ):
            # Mock individual encoding success
            with patch.object(
                service, "encode_text", side_effect=[[0.1, 0.2], [0.3, 0.4]]
            ):
                results = service.encode_batch(texts)

                assert results == [[0.1, 0.2], [0.3, 0.4]]
                assert service.encode_text.call_count == 2  # Called for each text

    def test_encode_query(self):
        """Test query encoding."""
        service = self._create_mock_service()
        mock_embedding = [0.1, 0.2, 0.3]

        with patch.object(service, "encode_text", return_value=mock_embedding):
            result = service.encode_query("search query")

            assert result == mock_embedding
            service.encode_text.assert_called_once_with("search query")

    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""
        service = self._create_mock_service()
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        with patch.object(service, "encode_text", return_value=mock_embedding):
            dimension = service.get_embedding_dimension()
            assert dimension == 5

    def test_get_embedding_dimension_fallback(self):
        """Test embedding dimension fallback on error."""
        service = self._create_mock_service()

        with patch.object(service, "encode_text", side_effect=Exception("Test error")):
            dimension = service.get_embedding_dimension()
            assert dimension == EMBEDDING_DIMENSION_DEFAULT

    def test_get_model_info(self):
        """Test getting model information."""
        service = self._create_mock_service()

        with patch.object(service, "get_embedding_dimension", return_value=384):
            info = service.get_model_info()

            assert info["model_name"] == service.model_name
            assert info["device"] == service.device
            assert info["batch_size"] == service.batch_size
            assert info["embedding_dimension"] == 384
            assert "cache_dir" in info

    def test_repr(self):
        """Test string representation."""
        with tempfile.TemporaryDirectory():
            service = EmbeddingService(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu",
                batch_size=8,
            )
            repr_str = repr(service)
            assert "EmbeddingService" in repr_str
            assert "all-MiniLM-L6-v2" in repr_str
            assert "cpu" in repr_str
            assert "8" in repr_str

    def _create_mock_service(self) -> EmbeddingService:
        """Create a service with mocked model for testing."""
        service = EmbeddingService.__new__(EmbeddingService)
        service.model_name = "test-model"
        service.device = "cpu"
        service.batch_size = 8
        service.cache_dir = Path("/tmp/cache")

        # Mock the model
        service._model = Mock()
        service._model.encode = Mock()

        return service


class TestEmbeddingServiceIntegration:
    """Integration tests for EmbeddingService with real models."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_model_encoding(self):
        """Test with a real (small) embedding model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            service = EmbeddingService(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu",
                batch_size=2,
                cache_dir=cache_dir,
            )

            # Test single encoding
            text = "This is a test sentence for embedding."
            embedding = service.encode_text(text)

            assert isinstance(embedding, list)
            assert len(embedding) > 0  # Should have dimension > 0
            assert all(isinstance(x, float) for x in embedding)

            # Test batch encoding
            texts = ["First sentence.", "Second sentence.", "Third sentence."]
            embeddings = service.encode_batch(texts)

            assert len(embeddings) == 3
            assert all(len(emb) == len(embedding) for emb in embeddings)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_batch_vs_single_consistency(self):
        """Test that batch and single encoding produce consistent results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            service = EmbeddingService(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu",
                batch_size=3,
                cache_dir=cache_dir,
            )

            texts = ["First text.", "Second text.", "Third text."]

            # Single encoding
            single_embeddings = [service.encode_text(text) for text in texts]

            # Batch encoding
            batch_embeddings = service.encode_batch(texts)

            # Results should be very similar (allowing for small numerical differences)
            for single, batch in zip(single_embeddings, batch_embeddings, strict=False):
                assert len(single) == len(batch)
                # Check that embeddings are reasonably similar
                # (exact equality might not hold due to floating point precision)
                similarity = sum(s * b for s, b in zip(single, batch, strict=False))
                assert similarity > 0.99  # Should be very similar
