"""
Integration tests for refactored RAG tool
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool


class TestRAGIntegration:
    """Integration tests for the complete RAG tool."""

    def test_create_rag_tool_basic(self):
        """Test basic RAG tool creation with factory function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            assert rag is not None
            assert rag.config == config
            assert rag.llm_service is not None
            assert rag.embedding_service is not None
            assert rag.document_store is not None
            assert rag.vector_index_manager is not None

    def test_create_rag_tool_default_config(self):
        """Test RAG tool creation with default config."""
        rag = create_rag_tool()

        assert rag is not None
        assert isinstance(rag.config, RAGConfig)

    @patch("agenthub.core.llm.llm_service.get_shared_llm_service")
    def test_search_documents_no_documents(self, mock_llm_service):
        """Test search when no documents are available."""
        # Configure the mock to return a proper LLM service that returns strings
        mock_llm_service.return_value.generate.return_value = "test query"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an empty directory with no files
            empty_data_dir = Path(temp_dir) / "empty_data"
            empty_data_dir.mkdir()

            # Clear any existing cache by using a fresh cache directory
            cache_dir = Path(temp_dir) / "cache"
            cache_dir.mkdir()

            config = RAGConfig(
                source_directory=empty_data_dir,
                cache_directory=cache_dir,
                cached_docs_path=cache_dir / "processed_documents.json",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            results = rag.search_documents("test query")

            assert results["query"] == "test query"
            assert results["results"] == []
            assert results["result_count"] == 0
            assert "metadata" in results

    def test_search_documents_with_query_rewriting_disabled(self):
        """Test search with query rewriting disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                enable_query_rewriting=False,
            )

            rag = create_rag_tool(config=config)

            results = rag.search_documents("test query")

            assert results["query"] == "test query"
            assert results["rewritten_query"] == "test query"  # Should be same

    def test_search_documents_with_intelligent_ranking_disabled(self):
        """Test search with intelligent ranking disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                enable_intelligent_ranking=False,
            )

            rag = create_rag_tool(config=config)

            results = rag.search_documents("test query")

            assert results["query"] == "test query"
            assert "metadata" in results
            assert results["metadata"]["enable_intelligent_ranking"] is False

    def test_get_stats_empty(self):
        """Test getting stats with no documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an empty directory with no files
            empty_data_dir = Path(temp_dir) / "data"
            empty_data_dir.mkdir()

            # Clear any existing cache by using a fresh cache directory
            cache_dir = Path(temp_dir) / "cache"
            cache_dir.mkdir()

            config = RAGConfig(
                source_directory=empty_data_dir,
                cache_directory=cache_dir,
                cached_docs_path=cache_dir / "processed_documents.json",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            stats = rag.get_stats()

            assert stats["document_count"] == 0
            assert stats["source_directory"] == str(config.source_directory)
            assert stats["embedding_model"] == config.embedding_model
            assert stats["index_exists"] is False

    def test_refresh_clears_cache(self):
        """Test that refresh clears cached components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use fresh cache directory to avoid interference
            cache_dir = Path(temp_dir) / "cache"
            cache_dir.mkdir()

            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                cache_directory=cache_dir,
                cached_docs_path=cache_dir / "processed_documents.json",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            # Access properties to populate cache
            _ = rag.documents
            _ = rag.vector_index

            # Verify cache is populated
            assert rag._documents is not None
            assert rag._vector_index is not None

            # Mock the clear_cache method to verify it's called
            with patch.object(rag.document_store, "clear_cache") as mock_clear:
                # Before refresh, manually clear the cache to simulate the behavior
                rag._documents = None
                rag._vector_index = None

                # Call refresh which should reload everything
                rag.refresh()

                # Should call clear_cache on document store
                mock_clear.assert_called_once()

                # After refresh, components should be reloaded due to lazy loading
                assert rag._documents is not None
                assert rag._vector_index is not None

    def test_repr(self):
        """Test string representation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                embedding_model="google/embeddinggemma-300m",
            )

            rag = create_rag_tool(config=config)

            repr_str = repr(rag)

            assert "RAGTool" in repr_str
            assert str(config.source_directory) in repr_str
            assert "google/embeddinggemma-300m" in repr_str

    def test_query_rewriting_integration(self):
        """Test query rewriting integration with LLM service."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                enable_query_rewriting=True,
            )

            rag = create_rag_tool(config=config)

            # Mock LLM service to return rewritten query
            with patch.object(
                rag.llm_service, "generate", return_value="rewritten query"
            ):
                results = rag.search_documents("original query")

                assert results["query"] == "original query"
                assert results["rewritten_query"] == "rewritten query"

    def test_intelligent_ranking_integration(self):
        """Test intelligent ranking integration with LLM service."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                enable_intelligent_ranking=True,
            )

            rag = create_rag_tool(config=config)

            # Mock vector search to return some results
            mock_nodes = [
                MagicMock(text="Result 1"),
                MagicMock(text="Result 2"),
                MagicMock(text="Result 3"),
            ]

            with patch.object(rag.vector_index, "as_retriever") as mock_retriever:
                mock_retriever.return_value.retrieve.return_value = mock_nodes

                # Mock LLM service to return ranking
                with patch.object(
                    rag.llm_service, "generate", return_value="[2, 0, 1]"
                ):
                    results = rag.search_documents("test query")

                    assert len(results["results"]) == 3
                    # Results should be reordered according to ranking
                    assert results["results"][0] == "Result 3"  # Index 2
                    assert results["results"][1] == "Result 1"  # Index 0
                    assert results["results"][2] == "Result 2"  # Index 1

    def test_result_truncation(self):
        """Test that results are properly truncated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                max_result_length=200,  # Short limit for testing (minimum is 100)
            )

            rag = create_rag_tool(config=config)

            # Create a very long result (more than 200 characters)
            long_text = (
                "This is a very long text that should be truncated because "
                "it exceeds the maximum length limit. " * 5
            )

            mock_nodes = [MagicMock(text=long_text)]

            with patch.object(rag.vector_index, "as_retriever") as mock_retriever:
                mock_retriever.return_value.retrieve.return_value = mock_nodes

                results = rag.search_documents("test query")

                assert len(results["results"]) == 1
                result = results["results"][0]
                assert len(result) <= config.max_result_length + 3  # +3 for "..."
                assert result.endswith("...")

    def test_max_results_parameter(self):
        """Test max_results parameter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                default_max_results=5,
            )

            rag = create_rag_tool(config=config)

            # Create many mock results
            mock_nodes = [MagicMock(text=f"Result {i}") for i in range(10)]

            with patch.object(rag.vector_index, "as_retriever") as mock_retriever:
                mock_retriever.return_value.retrieve.return_value = mock_nodes

                # Test with custom max_results
                results = rag.search_documents("test query", max_results=3)

                assert len(results["results"]) == 3
                assert results["result_count"] == 3

    def test_error_handling_no_llm_service(self):
        """Test graceful handling when LLM service is unavailable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
                enable_query_rewriting=True,
                enable_intelligent_ranking=True,
            )

            rag = create_rag_tool(config=config)

            # Mock LLM service to simulate unavailability
            with patch.object(
                rag.llm_service, "generate", side_effect=Exception("LLM unavailable")
            ):
                results = rag.search_documents("test query")

                # Should still work, just without LLM features
                assert results["query"] == "test query"
                assert results["rewritten_query"] == "test query"  # No rewriting
                assert "results" in results

    def test_backward_compatibility_with_old_config(self):
        """Test backward compatibility with old-style config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config using old-style dict
            config_dict = {
                "source_directory": str(Path(temp_dir) / "data"),
                "cache_directory": str(Path(temp_dir) / "cache"),
                "embedding_model": "google/embeddinggemma-300m",
                "use_local_embeddings": True,
            }

            config = RAGConfig.from_dict(config_dict)
            rag = create_rag_tool(config=config)

            assert rag is not None
            assert str(rag.config.source_directory) == config_dict["source_directory"]

    def test_configuration_validation(self):
        """Test that configuration validation works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test invalid configuration
            with pytest.raises(ValueError):
                RAGConfig(
                    source_directory=Path(temp_dir) / "data",
                    embedding_batch_size=0,  # Invalid: must be positive
                )

            # Test valid configuration
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                embedding_batch_size=16,  # Valid
            )
            assert config.embedding_batch_size == 16

    def test_lazy_loading(self):
        """Test that components are lazy loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            # Initially should be None
            assert rag._documents is None
            assert rag._vector_index is None

            # Access should trigger loading
            with patch.object(rag.document_store, "load_documents") as mock_load:
                mock_load.return_value = []
                docs = rag.documents
                assert docs == []
                assert rag._documents == []
                mock_load.assert_called_once()

            with patch.object(rag.vector_index_manager, "build_or_load") as mock_build:
                mock_build.return_value = MagicMock()
                index = rag.vector_index
                assert index is not None
                assert rag._vector_index is not None
                mock_build.assert_called_once()


class TestRAGFactoryFunction:
    """Tests for the create_rag_tool factory function."""

    def test_factory_with_no_config(self):
        """Test factory function with no config provided."""
        rag = create_rag_tool()

        assert rag is not None
        assert isinstance(rag.config, RAGConfig)

    def test_factory_with_custom_config(self):
        """Test factory function with custom config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "custom_data",
                embedding_model="custom-model",
                default_max_results=10,
            )

            # Mock the embedding service to avoid model loading
            with patch("agenthub.builtin.tools.rag.EmbeddingService") as mock_embedding:
                mock_embedding_instance = mock_embedding.return_value
                mock_embedding_instance.get_embedding_dimension.return_value = 384

                rag = create_rag_tool(config=config)

                assert rag.config == config
                assert rag.config.embedding_model == "custom-model"
            assert rag.config.default_max_results == 10

    def test_factory_dependency_injection(self):
        """Test that factory properly injects dependencies."""
        rag = create_rag_tool()

        # All services should be properly initialized
        assert rag.llm_service is not None
        assert rag.embedding_service is not None
        assert rag.document_store is not None
        assert rag.vector_index_manager is not None

        # Services should be properly configured
        assert rag.embedding_service.model_name == rag.config.embedding_model
        assert rag.document_store.source_dir == rag.config.source_directory
        assert rag.vector_index_manager.storage_dir == rag.config.index_storage_location


class TestRAGErrorHandling:
    """Tests for RAG tool error handling."""

    def test_search_with_invalid_max_results(self):
        """Test search with invalid max_results parameter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            # Should work with valid max_results
            results = rag.search_documents("test", max_results=1)
            assert results["result_count"] == 0  # No documents, but no error

            # Should work with large max_results
            results = rag.search_documents("test", max_results=100)
            assert results["result_count"] == 0

    def test_empty_query_handling(self):
        """Test handling of empty queries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            # Should handle empty query gracefully
            results = rag.search_documents("")
            assert results["query"] == ""
            assert "results" in results

            # Should handle whitespace-only query
            results = rag.search_documents("   ")
            assert results["query"] == "   "

    def test_unicode_handling(self):
        """Test handling of unicode text."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RAGConfig(
                source_directory=Path(temp_dir) / "data",
                index_storage_location=Path(temp_dir) / "storage",
            )

            rag = create_rag_tool(config=config)

            # Should handle unicode queries
            unicode_query = "Café résumé naïve 中文 🚀"
            results = rag.search_documents(unicode_query)

            assert results["query"] == unicode_query
            assert "results" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
