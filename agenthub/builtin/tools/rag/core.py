"""
Refactored RAG (Retrieval-Augmented Generation) Core

Clean orchestrator that coordinates between services for document retrieval.
Uses dependency injection and integrates with AgentHub CoreLLMService.
"""

import logging
import time
from typing import Any

from llama_index.core import Document, VectorStoreIndex

from .config import RAGConfig
from .document_store import DocumentStore
from .embeddings import EmbeddingService
from .vector_index import VectorIndexManager

logger = logging.getLogger(__name__)

# Constants for LLM prompts
QUERY_REWRITE_PROMPT = """
You are a great assistant that converts a user query to a retrieval query
to search for relevant information using text similarity. Focus on the intention
of the query to rewrite the best retrieval query.
"""

RANKING_PROMPT_TEMPLATE = """
You are a strict ranking engine. Given a user query and a list of passages
labeled with numeric IDs, return ONLY a JSON array of the IDs sorted from
most relevant to least relevant. Do not include any text outside the JSON array.

Query:
{query}

Passages (format: ID: text):
{passages}

Output format example: [2, 0, 1].
"""


class RAGTool:
    """
    Refactored RAG (Retrieval-Augmented Generation) tool for document retrieval.

    This is a clean orchestrator that:
    - Coordinates between services (dependency injection)
    - Executes search workflow
    - Provides public API
    - Handles high-level errors
    - Integrates with AgentHub CoreLLMService

    No direct file I/O, no global state, simple orchestration logic.
    """

    def __init__(
        self,
        config: RAGConfig,
        llm_service: Any,  # CoreLLMService
        embedding_service: EmbeddingService,
        document_store: DocumentStore,
        vector_index_manager: VectorIndexManager,
    ):
        """
        Initialize the RAG tool with dependency injection.

        Args:
            config: RAG configuration
            llm_service: AgentHub CoreLLMService instance
            embedding_service: Embedding service for text encoding
            document_store: Document store for document management
            vector_index_manager: Vector index manager for search
        """
        self.config = config
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.document_store = document_store
        self.vector_index_manager = vector_index_manager

        logger.info("Initialized RAGTool with dependency injection")
        logger.info(f"Config: {config}")
        logger.info(f"LLM Service: {llm_service.__class__.__name__}")
        logger.info(f"Embedding Service: {embedding_service}")

        # Lazy-loaded components
        self._documents: list[Document] | None = None
        self._vector_index: VectorStoreIndex | None = None

    @property
    def documents(self) -> list[Document]:
        """Get documents (lazy loaded)."""
        # Force reload if reindexing
        if self._documents is None or self.config.is_reindex:
            if self.config.is_reindex:
                logger.info(
                    "Reindex requested. Clearing cache and reloading "
                    "documents from source..."
                )
                self.document_store.clear_cache()
            else:
                logger.info("Loading documents...")
            self._documents = self.document_store.load_documents(
                force_reload=self.config.is_reindex
            )
            logger.info(f"Loaded {len(self._documents)} documents")
        return self._documents

    @property
    def vector_index(self) -> VectorStoreIndex:
        """Get vector index (lazy loaded)."""
        # Force rebuild if reindexing
        if self._vector_index is None or self.config.is_reindex:
            if self.config.is_reindex:
                logger.info("Reindex requested. Rebuilding index from scratch...")
            else:
                logger.info("Building/loading vector index...")
            self._vector_index = self.vector_index_manager.build_or_load(
                self.documents, force_rebuild=self.config.is_reindex
            )
            logger.info("Vector index ready")
        return self._vector_index

    def _rewrite_query(self, query: str) -> str:
        """
        Rewrite query for better retrieval using LLM service.

        Args:
            query: Original user query

        Returns:
            Rewritten query
        """
        if not self.config.enable_query_rewriting:
            return query

        if not self.llm_service:
            logger.info("Query rewriting disabled (no LLM service)")
            return query

        try:
            prompt = (
                f"User query: {query}\n"
                "Only return the converted retrieval query, no other text."
            )

            rewritten_query = self.llm_service.generate(
                input_data=prompt,
                system_prompt=QUERY_REWRITE_PROMPT,
                temperature=0.0,
            )

            rewritten_query = rewritten_query.strip()
            if rewritten_query:
                logger.info(f"Query rewritten: '{query}' -> '{rewritten_query}'")
                return rewritten_query
            else:
                logger.warning("Query rewriting returned empty result, using original")
                return query

        except Exception as e:
            logger.warning(f"Query rewriting failed: {e}. Using original query.")
            return query

    def _apply_intelligent_ranking(
        self, search_query: str, candidate_results: list[str]
    ) -> list[str]:
        """
        Apply intelligent ranking to search results using LLM service.

        Args:
            search_query: The search query
            candidate_results: List of candidate result texts

        Returns:
            Ranked list of results
        """
        if not candidate_results:
            return candidate_results

        if not self.config.enable_intelligent_ranking:
            logger.info("Intelligent ranking disabled")
            return candidate_results

        if not self.llm_service:
            logger.info("Intelligent ranking disabled (no LLM service)")
            return candidate_results

        start_time = time.time()

        try:
            # Format passages for ranking
            formatted_passages = "\n\n".join(
                [f"{idx}: {content}" for idx, content in enumerate(candidate_results)]
            )

            ranking_prompt = RANKING_PROMPT_TEMPLATE.format(
                query=search_query, passages=formatted_passages
            )

            # Get ranking from LLM
            ranking_response = self.llm_service.generate(
                input_data=ranking_prompt,
                temperature=0.0,
            )

            # Parse the response
            sorted_indices = self._parse_ranking_response(
                ranking_response, len(candidate_results)
            )

            if sorted_indices:
                ranked_results = [
                    candidate_results[i]
                    for i in sorted_indices
                    if i < len(candidate_results)
                ]
                elapsed = time.time() - start_time
                logger.info(
                    f"Intelligent ranking: {len(ranked_results)} results "
                    f"reordered in {elapsed:.2f}s"
                )
                return ranked_results
            else:
                logger.warning("Failed to parse ranking response, using original order")
                return candidate_results

        except Exception as e:
            logger.warning(f"Intelligent ranking failed: {e}. Using original order.")
            return candidate_results

        finally:
            elapsed_time = time.time() - start_time
            logger.debug(f"Intelligent ranking took {elapsed_time:.2f} seconds")

    def _parse_ranking_response(self, response: str, num_candidates: int) -> list[int]:
        """
        Parse the LLM ranking response to extract sorted indices.
        Handles various response formats robustly.

        Args:
            response: LLM response containing ranking
            num_candidates: Number of candidate results

        Returns:
            List of indices in ranked order
        """
        import json

        try:
            # Clean the response
            response_text = response.strip()

            # First, try to parse as JSON array
            if "[" in response_text and "]" in response_text:
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                json_str = response_text[start:end]

                try:
                    indices = json.loads(json_str)
                    if isinstance(indices, list):
                        # Validate indices
                        valid_indices = []
                        for idx in indices:
                            if isinstance(idx, int) and 0 <= idx < num_candidates:
                                valid_indices.append(idx)

                        if valid_indices:
                            return valid_indices
                except (json.JSONDecodeError, ValueError):
                    pass  # Fall through to text parsing

            # Fallback: Extract from text
            # (more robust parsing like reference implementation)
            # Split into lines and find the line with digits/brackets
            response_lines = response_text.split("\n")
            relevant_line = next(
                (
                    line_text
                    for line_text in response_lines
                    if any(char.isdigit() or char in "[]" for char in line_text)
                ),
                response_text,  # Use full response if no suitable line found
            )

            # Extract numbers from the relevant line
            sorted_indices = []
            for token_text in (
                relevant_line.replace(",", " ")
                .replace("[", " ")
                .replace("]", " ")
                .split()
            ):
                try:
                    index_value = int(token_text.strip())
                    if 0 <= index_value < num_candidates:
                        sorted_indices.append(index_value)
                except ValueError:
                    continue

            # Remove duplicates while preserving order
            seen = set()
            unique_indices = []
            for idx in sorted_indices:
                if idx not in seen:
                    seen.add(idx)
                    unique_indices.append(idx)

            if unique_indices:
                return unique_indices

        except Exception as e:
            logger.warning(f"Failed to parse ranking response: {e}")

        return []

    def _truncate_results(self, results: list[str], max_results: int) -> list[str]:
        """
        Truncate results to maximum length and count.

        Args:
            results: List of result texts
            max_results: Maximum number of results

        Returns:
            Truncated results
        """
        truncated = []
        for result in results[:max_results]:
            if len(result) > self.config.max_result_length:
                truncated.append(result[: self.config.max_result_length] + "...")
            else:
                truncated.append(result)
        return truncated

    def search_documents(
        self,
        query_text: str,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """
        Search for relevant documents using vector similarity and intelligent ranking.

        Args:
            query_text: The search query
            max_results: Maximum number of results to return

        Returns:
            Dictionary containing search results and metadata
        """
        # Use defaults from config if not specified
        num_results = max_results or self.config.default_max_results

        logger.info(
            f"Starting document search: '{query_text}' (max_results={num_results})"
        )

        # Rewrite query if enabled
        rewritten_query = self._rewrite_query(query_text)

        # Perform vector search
        document_retriever = self.vector_index.as_retriever(
            similarity_top_k=self.config.similarity_top_k
        )
        retrieved_nodes = document_retriever.retrieve(rewritten_query)
        text_results = [node.text for node in retrieved_nodes]

        logger.info(f"Vector search returned {len(text_results)} candidates")

        # Apply intelligent ranking
        ranked_results = self._apply_intelligent_ranking(rewritten_query, text_results)

        # Truncate results
        final_results = self._truncate_results(ranked_results, num_results)

        logger.info(f"Search completed: {len(final_results)} results")

        return {
            "query": query_text,
            "rewritten_query": (
                rewritten_query if rewritten_query != query_text else query_text
            ),
            "results": final_results,
            "result_count": len(final_results),
            "source_directory": str(self.config.source_directory),
            "metadata": {
                "embedding_model": self.config.embedding_model,
                "llm_model": self.config.get_effective_llm_model(),
                "use_local_embeddings": self.config.use_local_embeddings,
                "enable_query_rewriting": self.config.enable_query_rewriting,
                "enable_intelligent_ranking": self.config.enable_intelligent_ranking,
            },
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the RAG tool.

        Returns:
            Dictionary containing RAG tool statistics
        """
        return {
            "document_count": len(self.documents),
            "source_directory": str(self.config.source_directory),
            "cache_directory": str(self.config.cache_directory),
            "embedding_model": self.config.embedding_model,
            "llm_model": self.config.get_effective_llm_model(),
            "use_local_embeddings": self.config.use_local_embeddings,
            "index_storage_location": str(self.config.index_storage_location),
            "index_exists": self.vector_index_manager.index_exists(),
            "embedding_dimension": self.embedding_service.get_embedding_dimension(),
            "supported_extensions": list(self.config.supported_extensions),
        }

    def refresh(self) -> None:
        """
        Refresh the RAG tool by reloading documents and rebuilding index.
        """
        logger.info("Refreshing RAG tool...")

        # Clear cached components
        self._documents = None
        self._vector_index = None

        # Clear document cache
        self.document_store.clear_cache()

        # Force reload
        _ = self.documents  # This will trigger reload
        _ = self.vector_index  # This will trigger rebuild

        logger.info("RAG tool refreshed successfully")

    def __repr__(self) -> str:
        """String representation of the RAG tool."""
        return (
            f"RAGTool(source='{self.config.source_directory}', "
            f"embedding='{self.config.embedding_model}', "
            f"llm='{self.config.get_effective_llm_model()}')"
        )
