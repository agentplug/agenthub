from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool
from agenthub.core.tools import run_resources, tool


@tool(
    name="rag_search",
    description="Search documents using RAG (Retrieval Augmented Generation)",
)
def rag_search(query: str, max_results: int = 5) -> dict:
    config = RAGConfig(
        source_directory="./sample_docs",
        enable_query_rewriting=False,
        enable_intelligent_ranking=False,
    )
    rag = create_rag_tool(config=config)
    return rag.search_documents(query_text=query, max_results=max_results)


run_resources()
