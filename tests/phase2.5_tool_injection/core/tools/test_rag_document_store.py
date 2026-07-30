"""
Tests for RAG Document Store
"""

import pytest

pytest.importorskip(
    "llama_index.core",
    reason="RAG optional dependencies not installed (pip install agenthub-sdk[rag])",
)


import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from agenthub.builtin.tools.rag.document_store import DocumentStore


class TestDocumentStore:
    """Test suite for DocumentStore."""

    def test_initialization(self):
        """Test store initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            cache_path = Path(temp_dir) / "cache" / "documents.json"

            source_dir.mkdir()
            cache_path.parent.mkdir()

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=cache_path,
                supported_extensions={".txt", ".pdf"},
            )

            assert store.source_dir == source_dir
            assert store.cache_path == cache_path
            assert store.supported_extensions == {".txt", ".pdf"}

    def test_get_default_extensions(self):
        """Test getting default supported extensions."""
        store = self._create_test_store()
        extensions = store._get_default_extensions()

        assert isinstance(extensions, set)
        assert ".pdf" in extensions
        assert ".txt" in extensions
        assert ".docx" in extensions
        assert ".md" in extensions

    def test_validate_source_directory_missing(self):
        """Test validation with missing source directory."""
        store = self._create_test_store(source_exists=False)

        is_valid, message = store.validate_source_directory()

        assert not is_valid
        assert "does not exist" in message

    def test_validate_source_directory_not_dir(self):
        """Test validation with file instead of directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "source.txt"
            source_file.write_text("test content")

            store = DocumentStore(
                source_dir=source_file,
                cache_path=Path(temp_dir) / "cache.json",
            )

            is_valid, message = store.validate_source_directory()

            assert not is_valid
            assert "not a directory" in message

    def test_validate_source_directory_empty(self):
        """Test validation with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "empty_source"
            source_dir.mkdir()

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=Path(temp_dir) / "cache.json",
            )

            is_valid, message = store.validate_source_directory()

            assert not is_valid
            assert "No supported files found" in message

    def test_validate_source_directory_valid(self):
        """Test validation with valid source directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()

            # Create a test file
            test_file = source_dir / "test.txt"
            test_file.write_text("Test document content")

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=Path(temp_dir) / "cache.json",
            )

            is_valid, message = store.validate_source_directory()

            assert is_valid
            assert "Found 1 supported files" in message

    def test_scan_for_files(self):
        """Test scanning for supported files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()

            # Create test files
            (source_dir / "doc1.txt").write_text("Content 1")
            (source_dir / "doc2.pdf").write_text("Content 2")
            (source_dir / "image.jpg").write_text("Not supported")

            # Create subdirectory and file
            subdir = source_dir / "subdir"
            subdir.mkdir()
            (subdir / "doc3.md").write_text("Content 3")

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=Path(temp_dir) / "cache.json",
            )

            files = store._scan_for_files()

            # Should find 3 supported files (txt, pdf, md)
            assert len(files) == 3
            extensions = {f.suffix for f in files}
            assert extensions == {".txt", ".pdf", ".md"}

    def test_cache_exists_and_valid_empty(self):
        """Test cache validation with empty but valid cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cache_path.write_text("[]")  # Empty JSON array

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            assert store._cache_exists_and_valid()

    def test_cache_exists_and_valid_with_data(self):
        """Test cache validation with valid cached data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"

            # Create valid cache data
            cache_data = [
                {"text": "Document 1", "metadata": {"source": "doc1.txt"}},
                {"text": "Document 2", "metadata": {"source": "doc2.txt"}},
            ]
            cache_path.write_text(json.dumps(cache_data))

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            assert store._cache_exists_and_valid()

    def test_cache_exists_and_valid_invalid_json(self):
        """Test cache validation with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cache_path.write_text("invalid json content")

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            assert not store._cache_exists_and_valid()

    def test_cache_exists_and_valid_missing_fields(self):
        """Test cache validation with missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cache_path.write_text(
                json.dumps([{"text": "Document 1"}])
            )  # Missing metadata

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            assert not store._cache_exists_and_valid()

    def test_load_from_cache(self):
        """Test loading documents from cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"

            # Create valid cache data
            cache_data = [
                {"text": "Document 1 content", "metadata": {"source": "doc1.txt"}},
                {"text": "Document 2 content", "metadata": {"source": "doc2.txt"}},
            ]
            cache_path.write_text(json.dumps(cache_data))

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            documents = store._load_from_cache()

            assert len(documents) == 2
            assert documents[0].text == "Document 1 content"
            assert documents[0].metadata["source"] == "doc1.txt"
            assert documents[1].text == "Document 2 content"
            assert documents[1].metadata["source"] == "doc2.txt"

    def test_load_from_cache_invalid_json(self):
        """Test loading from cache with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cache_path.write_text("invalid json")

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            # Should fall back to source loading (which will return empty)
            documents = store._load_from_cache()
            assert documents == []

    @patch("agenthub.builtin.tools.rag.document_store.SimpleDirectoryReader")
    def test_load_from_source(self, mock_reader_class):
        """Test loading documents from source directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()

            # Create a test file
            test_file = source_dir / "test.txt"
            test_file.write_text("Test content")

            # Mock the reader
            mock_reader = Mock()
            mock_reader.load_data.return_value = [
                MagicMock(text="Test document", metadata={"source": "test.txt"})
            ]
            mock_reader_class.return_value = mock_reader

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=Path(temp_dir) / "cache.json",
            )

            documents = store._load_from_source()

            assert len(documents) == 1
            assert documents[0].text == "Test document"
            mock_reader_class.assert_called_once()
            mock_reader.load_data.assert_called_once()

    def test_load_from_source_no_files(self):
        """Test loading from source with no supported files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=Path(temp_dir) / "cache.json",
            )

            documents = store._load_from_source()
            assert documents == []

    def test_save_to_cache(self):
        """Test saving documents to cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            # Create mock documents
            doc1 = MagicMock()
            doc1.text = "Document 1 content"
            doc1.metadata = {"source": "doc1.txt"}

            doc2 = MagicMock()
            doc2.text = "Document 2 content"
            doc2.metadata = {"source": "doc2.txt"}

            documents = [doc1, doc2]

            store._save_to_cache(documents)

            # Verify cache was created
            assert cache_path.exists()

            # Load and verify content
            cached_data = json.loads(cache_path.read_text())
            assert len(cached_data) == 2
            assert cached_data[0]["text"] == "Document 1 content"
            assert cached_data[0]["metadata"]["source"] == "doc1.txt"

    def test_load_documents_from_cache(self):
        """Test load_documents using cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"

            # Create valid cache data
            cache_data = [
                {"text": "Cached document", "metadata": {"source": "cached.txt"}},
            ]
            cache_path.write_text(json.dumps(cache_data))

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            documents = store.load_documents()

            assert len(documents) == 1
            assert documents[0].text == "Cached document"

    def test_load_documents_force_reload(self):
        """Test load_documents with force reload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            cache_path = Path(temp_dir) / "cache.json"

            # Create cache with old data
            old_cache_data = [{"text": "Old cached", "metadata": {}}]
            cache_path.write_text(json.dumps(old_cache_data))

            # Create source file
            (source_dir / "new.txt").write_text("New content")

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=cache_path,
            )

            # Mock the source loading to return new documents
            with patch.object(store, "_load_from_source") as mock_load:
                mock_load.return_value = [
                    MagicMock(text="New document", metadata={"source": "new.txt"})
                ]

                documents = store.load_documents(force_reload=True)

                assert len(documents) == 1
                assert documents[0].text == "New document"
                mock_load.assert_called_once()

    def test_get_document_count(self):
        """Test getting document count."""
        store = self._create_test_store()

        with patch.object(store, "load_documents") as mock_load:
            mock_load.return_value = [MagicMock(), MagicMock(), MagicMock()]

            count = store.get_document_count()

            assert count == 3
            mock_load.assert_called_once()

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        store = DocumentStore(
            source_dir=Path("/tmp/source"),
            cache_path=Path("/tmp/cache.json"),
            supported_extensions={".txt", ".pdf"},
        )

        extensions = store.get_supported_extensions()

        assert extensions == {".txt", ".pdf"}
        # Should return a copy, not the original
        assert extensions is not store.supported_extensions

    def test_clear_cache(self):
        """Test clearing cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cache_path.write_text("test content")

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            result = store.clear_cache()

            assert result is True
            assert not cache_path.exists()

    def test_clear_cache_nonexistent(self):
        """Test clearing non-existent cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "nonexistent.json"

            store = DocumentStore(
                source_dir=Path(temp_dir) / "source",
                cache_path=cache_path,
            )

            result = store.clear_cache()

            assert result is True  # Should succeed even if file doesn't exist

    def test_get_stats(self):
        """Test getting store statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            (source_dir / "test.txt").write_text("Test content")

            cache_path = Path(temp_dir) / "cache.json"

            store = DocumentStore(
                source_dir=source_dir,
                cache_path=cache_path,
                supported_extensions={".txt"},
            )

            stats = store.get_stats()

            assert stats["source_directory"] == str(source_dir)
            assert stats["cache_path"] == str(cache_path)
            assert stats["supported_files_found"] == 1
            assert ".txt" in stats["supported_extensions"]
            assert stats["source_directory_exists"] is True

    def test_repr(self):
        """Test string representation."""
        store = DocumentStore(
            source_dir=Path("/tmp/source"),
            cache_path=Path("/tmp/cache.json"),
            supported_extensions={".txt", ".pdf"},
        )

        repr_str = repr(store)
        assert "DocumentStore" in repr_str
        assert "/tmp/source" in repr_str
        assert "/tmp/cache.json" in repr_str
        assert "2" in repr_str  # Number of extensions

    def _create_test_store(self, source_exists: bool = True) -> DocumentStore:
        """Create a test document store."""
        with tempfile.TemporaryDirectory() as temp_dir:
            if source_exists:
                source_dir = Path(temp_dir) / "source"
                source_dir.mkdir()
            else:
                source_dir = Path(temp_dir) / "nonexistent"

            cache_path = Path(temp_dir) / "cache.json"

            return DocumentStore(
                source_dir=source_dir,
                cache_path=cache_path,
            )
