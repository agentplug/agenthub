"""Tests for RAG tool functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

pytest.importorskip(
    "llama_index.core",
    reason="RAG optional dependencies not installed (pip install agenthub-sdk[rag])",
)

from agenthub.builtin.tools.rag import (  # noqa: E402
    RAGConfig,
    RAGTool,
    create_rag_tool,
)


class TestRAGConfig:
    """Test cases for RAGConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RAGConfig()
        # The validator converts relative paths to absolute paths
        assert config.source_directory.name == "data"  # Check the directory name
        assert config.use_local_embeddings is True
        assert config.embedding_batch_size == 8
        assert config.default_max_results == 5
        assert config.enable_query_rewriting is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RAGConfig(
            source_directory="./custom-data",
            embedding_batch_size=16,
            default_max_results=10,
        )
        # The validator converts relative paths to absolute paths
        assert config.source_directory.name == "custom-data"  # Check the directory name
        assert config.embedding_batch_size == 16
        assert config.default_max_results == 10

    def test_config_to_dict(self):
        """Test configuration conversion to dictionary."""
        config = RAGConfig(source_directory="./test")
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        # to_dict converts Path back to string
        assert config_dict["source_directory"].endswith("test")  # Check ends with test

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "source_directory": "./test",
            "embedding_batch_size": 16,
            "default_max_results": 10,
        }
        config = RAGConfig.from_dict(config_dict)
        # from_dict converts string to Path, validator converts to absolute
        assert config.source_directory.name == "test"  # Check directory name
        assert config.embedding_batch_size == 16
        assert config.default_max_results == 10

    def test_config_validation_positive(self):
        """Test configuration validation with valid values."""
        config = RAGConfig(
            source_directory="./data",
            embedding_batch_size=8,
            default_max_results=5,
        )
        # Should not raise any exception
        config.validate()

    def test_config_validation_negative(self):
        """Test configuration validation with invalid values."""
        from pydantic import ValidationError

        # Pydantic validates on creation, so we need to test the validation errors
        with pytest.raises(ValidationError):  # Pydantic will raise validation error
            RAGConfig(embedding_batch_size=0)  # Zero should fail validation

        with pytest.raises(ValidationError):  # Pydantic will raise validation error
            RAGConfig(default_max_results=-1)  # Negative should fail validation

        with pytest.raises(ValidationError):  # Pydantic will raise validation error
            RAGConfig(api_timeout_seconds=0)  # Zero should fail validation


class TestRAGTool:
    """Test cases for RAGTool class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    @pytest.fixture
    def temp_data_dir(self, temp_dir):
        """Create a temporary directory with test documents."""
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    def rag_config(self, temp_dir, temp_data_dir):
        """Create a RAG config for testing."""
        return RAGConfig(
            source_directory=temp_data_dir,
            cache_directory=str(Path(temp_dir) / "cache"),
            cached_docs_path=str(Path(temp_dir) / "cache" / "docs.json"),
            index_storage_location=str(Path(temp_dir) / "cache"),
            use_local_embeddings=True,
            embedding_batch_size=2,
        )

    @pytest.fixture
    def rag_tool_factory(self):
        """Factory for building RAGTool instances with mocked dependencies."""

        sentinel = object()

        def _factory(
            config: RAGConfig,
            *,
            documents: list | None = None,
            retriever_texts: list[str] | None = None,
            llm_service=sentinel,
            vector_index_exists: bool = True,
        ):
            document_store = Mock()
            document_store.load_documents.return_value = documents or []

            vector_index = Mock()
            retriever = Mock()
            retrieved_nodes = []
            for text in retriever_texts or []:
                node = Mock()
                node.text = text
                retrieved_nodes.append(node)
            retriever.retrieve.return_value = retrieved_nodes
            vector_index.as_retriever.return_value = retriever

            vector_index_manager = Mock()
            vector_index_manager.build_or_load.return_value = vector_index
            vector_index_manager.index_exists.return_value = vector_index_exists

            embedding_service = Mock()
            llm = llm_service if llm_service is not sentinel else Mock()

            tool = RAGTool(
                config=config,
                llm_service=llm,
                embedding_service=embedding_service,
                document_store=document_store,
                vector_index_manager=vector_index_manager,
            )

            return tool, {
                "document_store": document_store,
                "vector_index_manager": vector_index_manager,
                "retriever": retriever,
                "embedding_service": embedding_service,
                "llm_service": llm,
            }

        return _factory

    def test_rag_tool_initialization(self, rag_config, rag_tool_factory):
        """Test RAG tool initialization."""
        tool, _ = rag_tool_factory(rag_config)
        assert tool.config == rag_config

    def test_document_collection_initialization(self, rag_config, rag_tool_factory):
        """Test document loading."""
        sample_docs = ["Doc 1", "Doc 2"]
        tool, deps = rag_tool_factory(rag_config, documents=sample_docs)

        assert len(tool.documents) == len(sample_docs)
        deps["document_store"].load_documents.assert_called_once()

    def test_vector_index_building(self, rag_config, rag_tool_factory):
        """Test vector index build/load path."""
        documents = ["Doc"]
        tool, deps = rag_tool_factory(rag_config, documents=documents)

        first_index = tool.vector_index
        assert first_index is deps["vector_index_manager"].build_or_load.return_value
        deps["vector_index_manager"].build_or_load.assert_called_once_with(
            documents, force_rebuild=False
        )

        # Ensure cached instance is reused
        assert tool.vector_index is first_index

    def test_search_documents_without_llm(self, rag_config, rag_tool_factory):
        """Test document search without LLM reranking."""
        config = rag_config.model_copy(
            update={
                "enable_query_rewriting": False,
                "enable_intelligent_ranking": False,
            }
        )
        retriever_texts = ["Result about ML"]
        tool, _ = rag_tool_factory(
            config,
            retriever_texts=retriever_texts,
        )

        results = tool.search_documents(
            query_text="machine learning",
            max_results=5,
        )

        assert results["query"] == "machine learning"
        assert results["results"] == retriever_texts
        assert results["result_count"] == 1

    def test_search_documents_with_invalid_source(self, rag_tool_factory):
        """Test search when no documents are available."""
        config = RAGConfig(
            source_directory="/nonexistent/directory/that/does/not/exist"
        )
        tool, _ = rag_tool_factory(config, documents=[])

        assert len(tool.documents) == 0

    def test_get_stats(self, rag_config, rag_tool_factory):
        """Test getting tool statistics."""
        documents = ["Doc A", "Doc B"]
        tool, deps = rag_tool_factory(
            rag_config,
            documents=documents,
            vector_index_exists=True,
        )

        stats = tool.get_stats()

        assert stats["document_count"] == len(documents)
        assert stats["source_directory"] == str(rag_config.source_directory)
        assert stats["embedding_model"] == rag_config.embedding_model
        deps["vector_index_manager"].index_exists.assert_called_once()

    def test_intelligent_ranking_with_llm(self, rag_config, rag_tool_factory):
        """Test intelligent ranking when LLM is available."""
        llm = Mock()
        llm.generate.return_value = "[1, 0]"

        config = rag_config.model_copy(update={"enable_intelligent_ranking": True})
        tool, _ = rag_tool_factory(config, llm_service=llm)

        candidate_results = ["First result", "Second result"]
        ranked = tool._apply_intelligent_ranking("query", candidate_results)

        llm.generate.assert_called_once()
        assert ranked == ["Second result", "First result"]

    def test_intelligent_ranking_without_llm(self, rag_config, rag_tool_factory):
        """Test intelligent ranking gracefully handles missing LLM."""
        config = rag_config.model_copy(update={"enable_intelligent_ranking": True})
        tool, _ = rag_tool_factory(config, llm_service=None)

        candidate_results = ["First result", "Second result", "Third result"]
        ranked = tool._apply_intelligent_ranking("test query", candidate_results)

        assert ranked == candidate_results

    def test_rewrite_query(self, rag_config, rag_tool_factory):
        """Test query rewriting via LLM."""
        llm = Mock()
        llm.generate.return_value = "machine learning algorithms"

        config = rag_config.model_copy(update={"enable_query_rewriting": True})
        tool, _ = rag_tool_factory(config, llm_service=llm)

        rewritten = tool._rewrite_query("What is ML?")

        llm.generate.assert_called_once()
        assert rewritten == "machine learning algorithms"


@pytest.mark.integration
@pytest.mark.skipif(
    not pytest.importorskip("llama_index", minversion=None),
    reason="llama-index not installed",
)
class TestRAGIntegration:
    """Integration tests for RAG tool."""

    def test_end_to_end_search(self, temp_dir):
        """Test end-to-end document search."""
        # Create test data directory with documents
        data_dir = temp_dir / "data"
        data_dir.mkdir()

        # Create test documents
        (data_dir / "test1.txt").write_text(
            "Machine learning is a subset of artificial intelligence."
        )
        (data_dir / "test2.txt").write_text(
            "Neural networks are used in deep learning."
        )

        config = RAGConfig(
            source_directory=str(data_dir),
            cache_directory=str(temp_dir / "cache"),
            index_storage_location=str(temp_dir / "cache"),
            use_local_embeddings=True,
            embedding_batch_size=1,
        )

        # Create and search using factory to ensure dependencies are wired
        tool = create_rag_tool(config=config)

        results = tool.search_documents(
            query_text="machine learning",
            max_results=5,
        )

        assert "query" in results
        assert "results" in results
        assert "result_count" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
