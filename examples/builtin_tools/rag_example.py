"""Example usage of RAG (Retrieval-Augmented Generation) built-in tool.

This example demonstrates how to search documents using RAG with vector
similarity search, intelligent ranking, and support for multiple document
formats (PDF, TXT, DOCX, MD, etc.).

The refactored RAG tool uses dependency injection and provides better performance
with batch embedding processing and integration with AgentHub's CoreLLMService.

Dependencies:
- Install with: uv sync --extra rag
"""

from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool
from agenthub.core.tools import run_resources, tool


@tool(
    name="rag_search",
    description=(
        "Search documents using RAG with vector similarity search, "
        "intelligent ranking, and query rewriting"
    ),
)
def rag_search(
    query: str,
    max_results: int = 5,
    source_directory: str = "./data",
) -> dict:
    """Search documents using RAG.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)
        source_directory: Directory containing documents (default: "./data")

    Returns:
        Dictionary containing search results and metadata
    """
    # Create RAG tool using the factory function (recommended approach)
    config = RAGConfig(source_directory=source_directory)
    rag = create_rag_tool(config=config)

    return rag.search_documents(
        query_text=query,
        max_results=max_results,
    )


# Alternative: Simple usage without custom configuration
@tool(
    name="rag_search_simple",
    description="Simple RAG search using default configuration",
)
def rag_search_simple(query: str, max_results: int = 5) -> dict:
    """Simple RAG search with default configuration."""
    # Use factory function with default config
    rag = create_rag_tool()
    return rag.search_documents(query_text=query, max_results=max_results)


# Advanced usage with custom configuration
@tool(
    name="rag_search_advanced",
    description="Advanced RAG search with custom configuration",
)
def rag_search_advanced(
    query: str,
    max_results: int = 10,
    source_directory: str = "./my-docs",
    embedding_model: str = "google/embeddinggemma-300m",
    enable_query_rewriting: bool = True,
) -> dict:
    """Advanced RAG search with custom configuration options."""
    config = RAGConfig(
        source_directory=source_directory,
        embedding_model=embedding_model,
        default_max_results=max_results,
        enable_query_rewriting=enable_query_rewriting,
        enable_intelligent_ranking=True,
    )

    rag = create_rag_tool(config=config)
    return rag.search_documents(query_text=query, max_results=max_results)


# Tool for getting RAG statistics
@tool(
    name="rag_stats",
    description="Get RAG tool statistics and configuration",
)
def rag_stats() -> dict:
    """Get statistics about the RAG tool and indexed documents."""
    rag = create_rag_tool()
    return rag.get_stats()


# Tool for refreshing RAG index
@tool(
    name="rag_refresh",
    description="Refresh RAG tool by reloading documents and rebuilding index",
)
def rag_refresh() -> dict:
    """Refresh the RAG tool by reloading documents and rebuilding the vector index."""
    rag = create_rag_tool()
    rag.refresh()
    return {"status": "success", "message": "RAG index refreshed"}


# Example of using the new factory function directly
if __name__ == "__main__":
    print("RAG Tool Example - Factory Function Usage")
    print("=" * 50)

    # Basic usage with factory function
    print("1. Basic usage with factory function:")
    rag = create_rag_tool()
    print(f"   Created RAG tool: {rag}")

    # Advanced usage with custom configuration
    print("\n2. Advanced usage with custom configuration:")
    config = RAGConfig(
        source_directory="./my-documents",
        embedding_model="google/embeddinggemma-300m",
        default_max_results=10,
        enable_query_rewriting=True,
        enable_intelligent_ranking=True,
    )
    rag_advanced = create_rag_tool(config=config)
    print(f"   Created advanced RAG tool: {rag_advanced}")

    # Get statistics
    print("\n3. Getting RAG statistics:")
    stats = rag.get_stats()
    print(f"   Document count: {stats.get('document_count', 'N/A')}")
    print(f"   Embedding model: {stats.get('embedding_model', 'N/A')}")
    print(f"   Index exists: {stats.get('index_exists', 'N/A')}")

    print("\nTo use RAG tools in AgentHub, use the @tool decorator:")
    print("from agenthub.core.tools import tool")
    print("from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig")
    print("\nThen you can create custom tools like rag_search, rag_stats, rag_refresh")


run_resources()
