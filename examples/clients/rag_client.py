#!/usr/bin/env python3
"""
Simple RAG Client - Minimal MCP tool call example
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client


async def search_rag(
    query: str, max_results: int = 5, server_url: str = "http://127.0.0.1:8000"
):
    """
    Search documents using RAG tool via MCP.

    Args:
        query: Search query
        max_results: Maximum number of results
        server_url: MCP server URL

    Returns:
        Search results
    """
    sse_url = f"{server_url}/sse"

    async with sse_client(url=sse_url) as streams:
        async with ClientSession(*streams) as session:
            # Initialize session
            await session.initialize()

            # Call the RAG search tool
            result = await session.call_tool(
                "rag_search", arguments={"query": query, "max_results": max_results}
            )

            # Extract and parse result
            if result.content and len(result.content) > 0:
                content = result.content[0].text
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"content": content}

            return {"error": "No content returned"}


def main():
    """Example usage."""
    print("=" * 60)
    print("RAG Client - Simple Example")
    print("=" * 60)

    # Execute search
    query = "What is deepseek?"
    print(f"\nSearching for: {query}")

    result = asyncio.run(search_rag(query=query, max_results=3))

    # Display results
    if "results" in result:
        print(f"\nFound {len(result['results'])} results:\n")
        for i, doc in enumerate(result["results"], 1):
            print(f"Result {i}:")
            if isinstance(doc, dict):
                print(f"  File: {doc.get('file', 'N/A')}")
                print(f"  Score: {doc.get('score', 'N/A'):.4f}")
                content_preview = doc.get("content", "")[:200]
                print(f"  Content: {content_preview}...\n")
            else:
                # Handle string or other formats
                doc_str = str(doc)[:200]
                print(f"  {doc_str}...\n")
    else:
        print(f"\nResult: {result}")

    print("=" * 60)


if __name__ == "__main__":
    main()
