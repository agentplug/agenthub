#!/usr/bin/env python3
"""
Simple RAG Example - Focus on Core Functionality

This example demonstrates the basic RAG tool capabilities with minimal,
working code that focuses on actual document retrieval.
"""

from pathlib import Path

from agenthub.builtin.tools.rag import RAGConfig, create_rag_tool


def main():
    """Simple, working RAG demonstration."""
    print("🔍 RAG Document Search Tool")
    print("=" * 40)

    # Directory containing documents to search
    test_docs = Path("/Users/nguyennm/Project/agenthub/sample_docs")

    if not test_docs.exists():
        print(f"❌ Documents directory not found: {test_docs}")
        print("💡 Please add some documents to the directory and try again.")
        return

    # Count available documents
    files = [f.name for f in test_docs.iterdir() if f.is_file()]

    if not files:
        print(f"❌ No documents found in: {test_docs}")
        print("💡 Please add some documents (.txt, .md, .pdf, etc.) and try again.")
        return

    print(f"📁 Found {len(files)} documents: {files}")

    # Configure RAG for this directory
    config = RAGConfig(
        source_directory="/Users/nguyennm/Project/agenthub/sample_docs",
        enable_query_rewriting=True,  # Disable for faster results in demo
        enable_intelligent_ranking=True,  # Disable to avoid LLM timeouts in demo
        default_max_results=3,
        api_timeout_seconds=5,
    )

    # Create RAG tool
    rag = create_rag_tool(config=config)

    print("\n🔧 RAG Configuration:")
    print(f"   Source: {config.source_directory}")
    print(f"   Query rewriting: {config.enable_query_rewriting}")
    print(f"   Intelligent ranking: {config.enable_intelligent_ranking}")

    # Force document loading and indexing
    try:
        _ = rag.documents  # Load documents
        _ = rag.vector_index  # Build index

        stats = rag.get_stats()
        print("\n📊 Index Status:")
        print(f"   Documents indexed: {stats.get('document_count', 0)}")
        print(f"   Index exists: {stats.get('index_exists', False)}")
        print(f"   Cache directory: {stats.get('cache_directory', 'N/A')}")

    except Exception as e:
        print(f"❌ Error preparing index: {e}")
        return

    # Test simple searches
    test_queries = [
        "getting started with AgentHub",
        "RAG tool features",
        "how to load agents",
        "document search capabilities",
    ]

    print(f"\n{'='*40}")
    print("🔍 Test Searches:")
    print(f"{'='*40}")

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * (len(query) + 10))

        try:
            # Search documents
            results = rag.search_documents(query_text=query, max_results=3)

            # Check results structure
            if isinstance(results, dict):
                documents = results.get("results", [])
                query_used = results.get("rewritten_query", query)

                if documents:
                    print(f"✅ Found {len(documents)} relevant documents:")

                    for j, doc in enumerate(documents[:2], 1):  # Show top 2
                        # Handle different result formats
                        if isinstance(doc, str):
                            # Direct string result
                            text = doc[:200] + "..." if len(doc) > 200 else doc
                            print(f"\n   📄 Result {j}:")
                            print(f"      📝 {text}")
                        elif isinstance(doc, dict):
                            # Dictionary result with metadata
                            text = doc.get("text", doc.get("content", ""))
                            source = doc.get("source", "document")
                            score = doc.get("score", 0.0)

                            snippet = text[:200] + "..." if len(text) > 200 else text
                            print(f"\n   📄 Result {j} [{source}]:")
                            print(f"      🎯 Score: {score:.2f}")
                            print(f"      📝 {snippet}")
                        else:
                            # Fallback - just print what we got
                            print(f"\n   📄 Result {j}: {str(doc)[:100]}...")

                    print(f"   🔍 Used query: '{query_used}'")
                else:
                    print("❌ No relevant documents found")
            else:
                print(f"❌ Unexpected result format: {type(results)}")
                print(f"   Raw result: {str(results)[:200]}...")

        except Exception as e:
            print(f"❌ Search error: {e}")


if __name__ == "__main__":
    main()
