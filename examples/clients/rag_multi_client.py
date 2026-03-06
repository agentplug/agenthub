#!/usr/bin/env python3
"""
Multi-Client RAG Test - Test multiple independent queries from different clients

This script tests the ability to process multiple queries concurrently
from different client sessions, ensuring each request is independent.
"""

import asyncio
import json
import time

from mcp import ClientSession
from mcp.client.sse import sse_client


async def search_rag_with_timing(
    client_id: int,
    query: str,
    max_results: int = 5,
    server_url: str = "http://127.0.0.1:8000",
    global_start_time: float = 0.0,
) -> tuple[int, dict, float, float, float]:
    """
    Search documents using RAG tool via MCP with timing.

    Args:
        client_id: Unique identifier for this client
        query: Search query
        max_results: Maximum number of results
        server_url: MCP server URL
        global_start_time: Global start time for relative timing

    Returns:
        Tuple of (client_id, result, processing_time_seconds,
                 start_time_offset, end_time_offset)
    """
    sse_url = f"{server_url}/sse"
    request_start = time.time()
    start_offset = request_start - global_start_time

    try:
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
                        parsed_result = json.loads(content)
                    except json.JSONDecodeError:
                        parsed_result = {"content": content}
                else:
                    parsed_result = {"error": "No content returned"}

                request_end = time.time()
                processing_time = request_end - request_start
                end_offset = request_end - global_start_time
                return (
                    client_id,
                    parsed_result,
                    processing_time,
                    start_offset,
                    end_offset,
                )

    except Exception as e:
        request_end = time.time()
        processing_time = request_end - request_start
        end_offset = request_end - global_start_time
        return (client_id, {"error": str(e)}, processing_time, start_offset, end_offset)


async def run_concurrent_queries(
    queries: list[tuple[int, str]],
    max_results: int = 5,
    server_url: str = "http://127.0.0.1:8000",
    global_start_time: float = 0.0,
    print_as_complete: bool = True,
) -> list[tuple[int, dict, float, float, float]]:
    """
    Run multiple queries concurrently from independent clients.

    Args:
        queries: List of (client_id, query) tuples
        max_results: Maximum number of results per query
        server_url: MCP server URL
        global_start_time: Global start time for relative timing
        print_as_complete: If True, print results as they complete

    Returns:
        List of (client_id, result, processing_time, start_offset, end_offset) tuples
    """
    # Create tasks
    tasks = [
        asyncio.create_task(
            search_rag_with_timing(
                client_id, query, max_results, server_url, global_start_time
            )
        )
        for client_id, query in queries
    ]

    results = []
    # Process results as they complete (not waiting for all)
    for coro in asyncio.as_completed(tasks):
        try:
            result_data = await coro
            results.append(result_data)
            if print_as_complete:
                client_id, result, processing_time, start_offset, end_offset = (
                    result_data
                )
                # Find the query for this client
                query = next(q for cid, q in queries if cid == client_id)
                print(
                    f"⏱️  Client {client_id} | Query: {query[:40]}... | "
                    f"Processing Time: {processing_time:.4f}s"
                )
        except Exception as e:
            print(f"❌ Request failed: {e}")

    # Sort results by client_id for consistent output
    results.sort(key=lambda x: x[0])
    return results


def print_result(
    client_id: int,
    query: str,
    result: dict,
    processing_time: float,
    start_offset: float = 0.0,
    end_offset: float = 0.0,
):
    """Print formatted result for a client."""
    print(f"\n{'='*60}")
    print(f"Client {client_id} - Query: {query}")
    print(f"{'='*60}")
    print(f"⏱️  Processing Time: {processing_time:.4f} seconds")
    if start_offset > 0 or end_offset > 0:
        print(f"⏰ Started at: +{start_offset:.4f}s, Finished at: +{end_offset:.4f}s")

    if "error" in result:
        print(f"❌ Error: {result['error']}")
    elif "results" in result:
        print(f"✅ Found {len(result['results'])} results:")
        for i, doc in enumerate(result["results"], 1):
            print(f"\n  Result {i}:")
            if isinstance(doc, dict):
                print(f"    File: {doc.get('file', 'N/A')}")
                print(f"    Score: {doc.get('score', 'N/A'):.4f}")
                content_preview = doc.get("content", "")[:150]
                print(f"    Content: {content_preview}...")
            else:
                doc_str = str(doc)[:150]
                print(f"    {doc_str}...")
    else:
        print(f"📄 Result: {result}")


def main():
    """Run multi-client test."""
    print("=" * 60)
    print("Multi-Client RAG Test")
    print("=" * 60)
    print("\nTesting concurrent queries from independent clients...\n")

    # Define test queries - each will be run by an independent client
    # Testing with 30 concurrent clients
    test_queries = [
        (1, "What is machine learning?"),
        (2, "What is deepseek?"),
        (3, "What is artificial intelligence?"),
        (4, "How does neural network work?"),
        (5, "What is transformer architecture?"),
        (6, "What is reinforcement learning?"),
        (7, "How do large language models work?"),
        (8, "What is attention mechanism?"),
        (9, "What is fine-tuning in AI?"),
        (10, "What is prompt engineering?"),
    ]

    print(f"Total queries: {len(test_queries)}")
    print("Starting all queries concurrently...\n")
    print("Processing times (as each request completes):")
    print("-" * 60)

    # Record global start time
    global_start_time = time.time()

    # Run all queries concurrently - results printed as they complete
    results = asyncio.run(
        run_concurrent_queries(
            test_queries,
            max_results=3,
            global_start_time=global_start_time,
            print_as_complete=True,
        )
    )
    total_time = time.time() - global_start_time

    print("-" * 60)
    print(f"\n{'='*60}")
    print("Summary - Individual Processing Times")
    print(f"{'='*60}")

    # Print just the processing times summary
    for client_id, result, processing_time, _start_offset, _end_offset in results:
        query = next(q for cid, q in test_queries if cid == client_id)
        status = "✅" if "error" not in result else "❌"
        print(f"{status} Client {client_id}: {processing_time:.4f}s - {query}")

    print(f"\n{'='*60}")
    print("Detailed Results")
    print(f"{'='*60}")

    # Print detailed results for each client
    for client_id, result, processing_time, start_offset, end_offset in results:
        # Find the original query for this client
        query = next(q for cid, q in test_queries if cid == client_id)
        print_result(
            client_id, query, result, processing_time, start_offset, end_offset
        )

    # Print summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Total queries: {len(results)}")
    print(f"Total wall-clock time: {total_time:.4f} seconds")
    avg_time = sum(t for _, _, t, _, _ in results) / len(results)
    print(f"Average processing time per query: {avg_time:.4f} seconds")

    # Calculate concurrency efficiency
    total_processing_time = sum(t for _, _, t, _, _ in results)
    efficiency = (total_processing_time / total_time) if total_time > 0 else 0
    print(f"Concurrency efficiency: {efficiency:.2f}x (higher is better)")
    print(f"  - If sequential: would take ~{total_processing_time:.4f}s")
    print(f"  - Actual concurrent: took {total_time:.4f}s")

    print("\nIndividual processing times:")
    for client_id, _, processing_time, start_offset, end_offset in results:
        query = next(q for cid, q in test_queries if cid == client_id)
        print(
            f"  Client {client_id} ({query[:30]}...): "
            f"{processing_time:.4f}s "
            f"(start: +{start_offset:.4f}s, end: +{end_offset:.4f}s)"
        )

    # Check if queries were truly independent (processing times should vary)
    times = [t for _, _, t, _, _ in results]
    start_offsets = [so for _, _, _, so, _ in results]
    end_offsets = [eo for _, _, _, _, eo in results]

    print("\nTime statistics:")
    print(f"  Fastest: {min(times):.4f}s")
    print(f"  Slowest: {max(times):.4f}s")
    print(f"  Range: {max(times) - min(times):.4f}s")
    print("\nConcurrency analysis:")
    print(f"  First request started: +{min(start_offsets):.4f}s")
    print(f"  Last request finished: +{max(end_offsets):.4f}s")
    print(f"  Overlap time: {max(end_offsets) - min(start_offsets):.4f}s")

    # Check if requests overlapped
    if max(start_offsets) < min(end_offsets):
        print("  ✅ Requests overlapped (true concurrency)")
    else:
        print("  ⚠️  Requests may have been sequential")

    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
