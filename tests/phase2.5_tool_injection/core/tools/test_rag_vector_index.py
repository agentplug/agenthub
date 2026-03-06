"""
Tests for RAG Vector Index Manager
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from agenthub.builtin.tools.rag.vector_index import VectorIndexManager


class TestVectorIndexManager:
    """Test suite for VectorIndexManager."""

    def test_initialization(self):
        """Test manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"

            manager = VectorIndexManager(storage_dir=storage_dir)

            assert manager.storage_dir == storage_dir
            assert storage_dir.exists()  # Should create directory

    @patch("agenthub.builtin.tools.rag.vector_index.VectorStoreIndex")
    def test_build_or_load_empty_documents(self, mock_index_class):
        """Test building with empty document list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock empty index
            mock_index = Mock()
            mock_index_class.return_value = mock_index

            documents = []
            result = manager.build_or_load(documents)

            assert result == mock_index
            mock_index_class.assert_called_once_with([])

    @patch("agenthub.builtin.tools.rag.vector_index.VectorStoreIndex")
    def test_build_or_load_new_index(self, mock_index_class):
        """Test building a new index when none exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock documents
            documents = [MagicMock(), MagicMock()]

            # Mock index creation
            mock_index = Mock()
            mock_index.storage_context = Mock()
            mock_index.storage_context.persist = Mock()
            mock_index_class.from_documents.return_value = mock_index

            # Test building new index
            result = manager.build_or_load(documents)

            assert result == mock_index
            mock_index_class.from_documents.assert_called_once_with(documents)
            mock_index.storage_context.persist.assert_called_once()

    @patch("agenthub.builtin.tools.rag.vector_index.load_index_from_storage")
    @patch("agenthub.builtin.tools.rag.vector_index.StorageContext")
    def test_build_or_load_existing_index(self, mock_storage_class, mock_load_index):
        """Test loading existing valid index."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock documents
            documents = [MagicMock(), MagicMock()]

            # Mock existing index
            mock_index = Mock()
            mock_index.docstore = Mock()
            mock_index.docstore.docs = {1: Mock(), 2: Mock()}  # 2 documents
            mock_load_index.return_value = mock_index

            # Mock storage context
            mock_storage = Mock()
            mock_storage_class.from_defaults.return_value = mock_storage

            # Create required index files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")

            result = manager.build_or_load(documents)

            assert result == mock_index
            # Called once in _is_index_valid and once in _load_from_storage
            assert mock_storage_class.from_defaults.call_count == 2
            # Called once in _is_index_valid and once in _load_from_storage
            assert mock_load_index.call_count == 2

    def test_is_index_valid_no_index(self):
        """Test index validation when no index exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            documents = [MagicMock(), MagicMock()]

            assert not manager._is_index_valid(documents)

    def test_is_index_valid_document_count_mismatch(self):
        """Test index validation with document count mismatch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Create required index files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")

            # Mock loading existing index with different document count
            with patch.object(manager, "_load_from_storage") as mock_load:
                mock_index = Mock()
                mock_index.docstore = Mock()
                mock_index.docstore.docs = {1: Mock()}  # 1 document
                mock_load.return_value = mock_index

                documents = [MagicMock(), MagicMock()]  # 2 documents

                assert not manager._is_index_valid(documents)

    @patch("agenthub.builtin.tools.rag.vector_index.load_index_from_storage")
    @patch("agenthub.builtin.tools.rag.vector_index.StorageContext")
    def test_load_from_storage_success(self, mock_storage_class, mock_load_index):
        """Test successful loading from storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock index
            mock_index = Mock()
            mock_load_index.return_value = mock_index

            # Mock storage context
            mock_storage = Mock()
            mock_storage_class.from_defaults.return_value = mock_storage

            result = manager._load_from_storage()

            assert result == mock_index
            mock_storage_class.from_defaults.assert_called_once_with(
                persist_dir=storage_dir
            )
            mock_load_index.assert_called_once_with(mock_storage)

    def test_load_from_storage_failure(self):
        """Test loading from storage with failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock storage context failure
            with patch(
                "agenthub.builtin.tools.rag.vector_index.StorageContext"
            ) as mock_storage_class:
                mock_storage_class.from_defaults.side_effect = Exception(
                    "Storage error"
                )

                result = manager._load_from_storage()

                # Should return empty index on failure
                assert isinstance(result, Mock)  # VectorStoreIndex is mocked

    @patch("agenthub.builtin.tools.rag.vector_index.VectorStoreIndex")
    def test_build_index_success(self, mock_index_class):
        """Test successful index building."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            documents = [MagicMock(), MagicMock()]
            mock_index = Mock()
            mock_index_class.from_documents.return_value = mock_index

            result = manager._build_index(documents)

            assert result == mock_index
            mock_index_class.from_documents.assert_called_once_with(documents)

    @patch("agenthub.builtin.tools.rag.vector_index.VectorStoreIndex")
    def test_build_index_failure(self, mock_index_class):
        """Test index building with failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            documents = [MagicMock(), MagicMock()]
            mock_index_class.from_documents.side_effect = Exception("Build error")

            result = manager._build_index(documents)

            # Should return empty index on failure
            assert isinstance(result, Mock)  # VectorStoreIndex is mocked

    @patch("agenthub.builtin.tools.rag.vector_index.VectorStoreIndex")
    def test_persist_success(self, mock_index_class):
        """Test successful index persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock index with storage context
            mock_index = Mock()
            mock_storage_context = Mock()
            mock_storage_context.persist = Mock()
            mock_index.storage_context = mock_storage_context

            manager._persist(mock_index)

            mock_storage_context.persist.assert_called_once_with(
                persist_dir=storage_dir
            )

    def test_persist_failure(self):
        """Test index persistence with failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock index with failing storage context
            mock_index = Mock()
            mock_storage_context = Mock()
            mock_storage_context.persist.side_effect = Exception("Persist error")
            mock_index.storage_context = mock_storage_context

            # Should not raise exception
            manager._persist(mock_index)

    def test_index_exists_true(self):
        """Test index existence check when index exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create required index files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")

            manager = VectorIndexManager(storage_dir=storage_dir)

            assert manager.index_exists()

    def test_index_exists_false(self):
        """Test index existence check when index doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            manager = VectorIndexManager(storage_dir=storage_dir)

            assert not manager.index_exists()

    def test_index_exists_partial(self):
        """Test index existence check with partial files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create only some required files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            # Missing vector_store.json

            manager = VectorIndexManager(storage_dir=storage_dir)

            assert not manager.index_exists()

    def test_clear_index_success(self):
        """Test successful index clearing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create index files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")
            (storage_dir / "graph_store.json").write_text("{}")

            manager = VectorIndexManager(storage_dir=storage_dir)

            result = manager.clear_index()

            assert result is True
            assert not (storage_dir / "docstore.json").exists()
            assert not (storage_dir / "index_store.json").exists()
            assert not (storage_dir / "vector_store.json").exists()
            assert not (storage_dir / "graph_store.json").exists()

    def test_clear_index_nonexistent(self):
        """Test clearing non-existent index."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            manager = VectorIndexManager(storage_dir=storage_dir)

            result = manager.clear_index()

            assert result is True  # Should succeed even if files don't exist

    def test_clear_index_failure(self):
        """Test index clearing with failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create a file
            (storage_dir / "docstore.json").write_text("{}")

            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock Path.unlink to raise exception
            with patch.object(Path, "unlink", side_effect=OSError("Permission denied")):
                result = manager.clear_index()

                # Should handle the error gracefully and return False
                assert result is False

    def test_get_index_stats_no_index(self):
        """Test getting stats when no index exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            stats = manager.get_index_stats()

            assert stats["storage_dir"] == str(storage_dir)
            assert stats["index_exists"] is False
            assert "document_count" not in stats

    @patch("agenthub.builtin.tools.rag.vector_index.load_index_from_storage")
    @patch("agenthub.builtin.tools.rag.vector_index.StorageContext")
    def test_get_index_stats_with_index(self, mock_storage_class, mock_load_index):
        """Test getting stats with existing index."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create index files with some content
            (storage_dir / "docstore.json").write_text(
                '{"a": "b"}' * 100
            )  # Larger file
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")

            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock loaded index
            mock_index = Mock()
            mock_index.docstore = Mock()
            mock_index.docstore.docs = {1: Mock(), 2: Mock(), 3: Mock()}  # 3 documents
            mock_load_index.return_value = mock_index

            stats = manager.get_index_stats()

            assert stats["storage_dir"] == str(storage_dir)
            assert stats["index_exists"] is True
            assert stats["document_count"] == 3
            assert stats["storage_size_bytes"] >= 0
            assert stats["storage_size_mb"] >= 0

    def test_get_index_stats_load_failure(self):
        """Test getting stats when index loading fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            storage_dir.mkdir()

            # Create index files
            (storage_dir / "docstore.json").write_text("{}")
            (storage_dir / "index_store.json").write_text("{}")
            (storage_dir / "vector_store.json").write_text("{}")

            manager = VectorIndexManager(storage_dir=storage_dir)

            # Mock loading failure
            with patch.object(
                manager, "_load_from_storage", side_effect=Exception("Load failed")
            ):
                stats = manager.get_index_stats()

                assert stats["storage_dir"] == str(storage_dir)
                assert stats["index_exists"] is True
                assert "error" in stats

    def test_repr(self):
        """Test string representation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"
            manager = VectorIndexManager(storage_dir=storage_dir)

            repr_str = repr(manager)

            assert "VectorIndexManager" in repr_str
            assert str(storage_dir) in repr_str
            assert "False" in repr_str  # index_exists should be False


class TestVectorIndexManagerIntegration:
    """Integration tests for VectorIndexManager with real components."""

    @pytest.mark.integration
    def test_full_index_lifecycle(self):
        """Test complete index lifecycle: build, persist, load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / "storage"

            # Create mock documents
            documents = []
            for i in range(3):
                doc = Mock()
                doc.text = f"This is test document {i}."
                doc.metadata = {"source": f"doc{i}.txt"}
                documents.append(doc)

            manager = VectorIndexManager(storage_dir=storage_dir)

            # Build index
            index = manager.build_or_load(documents)

            assert index is not None
            assert manager.index_exists()

            # Load existing index
            loaded_index = manager.build_or_load(documents)

            assert loaded_index is not None
            assert manager.index_exists()

            # Clear index
            result = manager.clear_index()
            assert result is True
            assert not manager.index_exists()
