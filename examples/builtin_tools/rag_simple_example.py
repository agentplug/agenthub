from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool
from agenthub.core.tools import run_resources, tool

"""
RAG Tool Example - Demonstrates embedding configuration

This example shows:
- Default OpenAI embeddings usage (text-embedding-3-small)
- How to configure local embeddings if needed

For local embeddings, uncomment the use_local_embeddings line.
OpenAI embeddings require OPENAI_API_KEY environment variable.
"""

config = RAGConfig(
    source_directory="./sample_docs",
    enable_query_rewriting=False,
    enable_intelligent_ranking=False,
    # To use local embeddings instead, add:
    # use_local_embeddings=True,
    # embedding_model="google/embeddinggemma-300m",
)
rag = create_rag_tool(config=config)


@tool(
    name="rag_search",
    description="Search documents using RAG (Retrieval Augmented Generation)",
)
def rag_search(query: str, max_results: int = 5) -> dict:
    # Uses OpenAI embeddings by default
    return rag.search_documents(query_text=query, max_results=max_results)


run_resources()
