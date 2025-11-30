"""
Document Store for RAG Tool

Provides document loading, caching, and validation functionality.
"""

import json
import logging
from pathlib import Path

from llama_index.core import Document

logger = logging.getLogger(__name__)


class DocumentStore:
    """
    Document store for loading, caching, and managing documents.

    Responsibilities:
    - Scan source directories for supported file types
    - Load documents using SimpleDirectoryReader
    - Cache processed documents to JSON
    - Validate document collections (empty, missing dirs)
    - Track metadata and processing stats
    """

    def __init__(
        self,
        source_dir: Path,
        cache_path: Path,
        supported_extensions: set[str] | None = None,
    ):
        """
        Initialize the document store.

        Args:
            source_dir: Directory containing source documents
            cache_path: Path to cache processed documents
            supported_extensions: Set of supported file extensions (optional)
        """
        self.source_dir = source_dir
        self.cache_path = cache_path
        self.supported_extensions = (
            supported_extensions or self._get_default_extensions()
        )

        # Ensure cache directory exists
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized DocumentStore")
        logger.info(f"Source directory: {self.source_dir}")
        logger.info(f"Cache path: {self.cache_path}")
        logger.info(f"Supported extensions: {len(self.supported_extensions)} formats")

    def _get_default_extensions(self) -> set[str]:
        """Get the default set of supported file extensions."""
        return {
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

    def validate_source_directory(self) -> tuple[bool, str]:
        """
        Validate the source directory.

        Returns:
            Tuple of (is_valid, message)
        """
        if not self.source_dir.exists():
            return False, f"Source directory does not exist: {self.source_dir}"

        if not self.source_dir.is_dir():
            return False, f"Source path is not a directory: {self.source_dir}"

        # Check for supported files
        files = self._scan_for_files()
        if not files:
            return False, f"No supported files found in: {self.source_dir}"

        return True, f"Found {len(files)} supported files"

    def _scan_for_files(self) -> list[Path]:
        """Scan the source directory for supported files."""
        try:
            files = [
                f
                for f in self.source_dir.rglob("*")
                if f.is_file() and f.suffix.lower() in self.supported_extensions
            ]
            return files
        except Exception as e:
            logger.error(f"Error scanning directory {self.source_dir}: {e}")
            return []

    def load_documents(self, force_reload: bool = False) -> list[Document]:
        """
        Load documents from source directory or cache.

        Args:
            force_reload: Force reload from source directory, ignoring cache

        Returns:
            List of Document objects
        """
        # Check if we should use cache
        if not force_reload and self._cache_exists_and_valid():
            logger.info(f"Loading documents from cache: {self.cache_path}")
            return self._load_from_cache()

        # Load from source directory
        logger.info(f"Loading documents from source directory: {self.source_dir}")
        documents = self._load_from_source()

        # Cache the documents if we loaded any
        if documents:
            logger.info(
                f"Saving {len(documents)} documents to cache: {self.cache_path}"
            )
            self._save_to_cache(documents)
        else:
            logger.warning("No documents loaded, cache not updated")

        return documents

    def _cache_exists_and_valid(self) -> bool:
        """Check if cache exists and is valid."""
        if not self.cache_path.exists():
            return False

        try:
            # Check if cache file is valid JSON
            with open(self.cache_path, encoding="utf-8") as f:
                data = json.load(f)

            # Basic validation
            if not isinstance(data, list):
                return False

            if not data:  # Empty cache is valid but we should reload
                return True

            # Check if first item has required fields
            first_item = data[0]
            if not isinstance(first_item, dict):
                return False

            required_fields = ["text", "metadata"]
            if not all(field in first_item for field in required_fields):
                return False

            return True

        except (json.JSONDecodeError, OSError, KeyError) as e:
            logger.warning(f"Cache validation failed: {e}")
            return False

    def _load_from_cache(self) -> list[Document]:
        """Load documents from cache."""
        try:
            with open(self.cache_path, encoding="utf-8") as f:
                cached_data = json.load(f)

            documents = [
                Document(text=doc_item["text"], metadata=doc_item.get("metadata", {}))
                for doc_item in cached_data
            ]

            logger.info(f"Loaded {len(documents)} documents from cache")
            return documents

        except Exception as e:
            logger.error(f"Failed to load documents from cache: {e}")
            logger.warning("Falling back to source directory loading")
            return self._load_from_source()

    def _load_from_source(self) -> list[Document]:
        """Load documents from the source directory."""
        # Validate source directory
        is_valid, message = self.validate_source_directory()
        if not is_valid:
            logger.warning(message)
            return []

        try:
            # Scan for files
            files = self._scan_for_files()
            if not files:
                logger.warning(f"No supported files found in: {self.source_dir}")
                return []

            logger.info(f"Processing {len(files)} documents from: {self.source_dir}")

            documents = []
            for file_path in files:
                try:
                    # Skip hidden files and directories
                    if file_path.name.startswith("."):
                        continue

                    # For PDFs and complex documents, use more robust loading
                    if file_path.suffix.lower() == ".pdf":
                        try:
                            from llama_index.core.readers import PDFReader

                            reader = PDFReader()
                            doc = reader.load_data(file_path)
                            documents.extend(doc)
                        except ImportError:
                            try:
                                # Try alternative import path
                                from llama_index.readers.file import PDFReader

                                reader = PDFReader()
                                doc = reader.load_data(file_path)
                                documents.extend(doc)
                            except ImportError:
                                # Fallback: skip PDF with warning
                                logger.warning(
                                    f"PDF reader not available, "
                                    f"skipping file: {file_path}"
                                )
                                continue
                    else:
                        # For simple text files, read directly
                        if file_path.suffix.lower() in [".txt", ".md"]:
                            with open(
                                file_path, encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                if content.strip():  # Only add non-empty content
                                    doc = Document(
                                        text=content,
                                        metadata={
                                            "file_name": file_path.name,
                                            "file_path": str(file_path),
                                            "file_type": file_path.suffix.lower(),
                                        },
                                    )
                                    documents.append(doc)
                        else:
                            # Use SimpleDirectoryReader for other formats
                            from llama_index.core import SimpleDirectoryReader

                            reader = SimpleDirectoryReader(
                                input_files=[str(file_path)], encoding="utf-8"
                            )
                            docs = reader.load_data()
                            # Add file metadata if not present
                            for doc in docs:
                                if not hasattr(doc, "metadata") or not doc.metadata:
                                    doc.metadata = {
                                        "file_name": file_path.name,
                                        "file_path": str(file_path),
                                        "file_type": file_path.suffix.lower(),
                                    }
                            documents.extend(docs)

                except Exception as file_error:
                    logger.warning(f"Failed to load file {file_path}: {file_error}")
                    continue

            logger.info(f"Successfully loaded {len(documents)} documents")
            return documents

        except Exception as e:
            logger.error(f"Failed to load documents from source: {e}")
            return []

    def _save_to_cache(self, documents: list[Document]) -> None:
        """Save documents to cache."""
        try:
            # Serialize documents
            serialized_documents = []
            for doc in documents:
                serialized_doc = {
                    "text": doc.text,
                    "metadata": doc.metadata if hasattr(doc, "metadata") else {},
                }
                serialized_documents.append(serialized_doc)

            # Save to cache
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(serialized_documents, f, indent=2, ensure_ascii=False)

            logger.info(f"Cached {len(documents)} documents to: {self.cache_path}")

        except Exception as e:
            logger.error(f"Failed to save documents to cache: {e}")
            # Don't fail if caching fails - documents are still loaded

    def get_document_count(self) -> int:
        """
        Get the number of documents in the store.

        Returns:
            Number of documents
        """
        try:
            documents = self.load_documents()
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0

    def get_supported_extensions(self) -> set[str]:
        """
        Get the set of supported file extensions.

        Returns:
            Set of supported extensions
        """
        return self.supported_extensions.copy()

    def clear_cache(self) -> bool:
        """
        Clear the document cache.

        Returns:
            True if cache was cleared successfully
        """
        try:
            if self.cache_path.exists():
                self.cache_path.unlink()
                logger.info(f"Cleared document cache: {self.cache_path}")
                return True
            return True  # No cache to clear
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get statistics about the document store.

        Returns:
            Dictionary with store statistics
        """
        document_count = self.get_document_count()
        files = self._scan_for_files()

        return {
            "source_directory": str(self.source_dir),
            "cache_path": str(self.cache_path),
            "document_count": document_count,
            "supported_files_found": len(files),
            "supported_extensions": list(self.supported_extensions),
            "cache_exists": self.cache_path.exists(),
            "source_directory_exists": self.source_dir.exists(),
        }

    def __repr__(self) -> str:
        """String representation of the document store."""
        return (
            f"DocumentStore(source_dir='{self.source_dir}', "
            f"cache_path='{self.cache_path}', "
            f"extensions={len(self.supported_extensions)})"
        )
