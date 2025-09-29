#!/usr/bin/env python3
"""
AgentHub Search Tool Server - Web Search Tool Example

This example demonstrates a focused MCP server that provides web search capabilities
using DuckDuckGo search with content extraction.
"""

import os

from agenthub.config import get_config
from agenthub.core.tools import get_available_tools, run_resources, tool


def _load_model_name() -> str:
    """
    Automatically detect and return the best available model based on API keys.
    Follows aisuite provider format: <provider>:<model-name>

    Returns:
        str: Model identifier in aisuite format
    """
    # Priority order: Check API keys and return corresponding model
    # OpenAI models
    if os.getenv("OPENAI_API_KEY"):
        return "openai:gpt-4o-mini"

    # Anthropic models
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic:claude-3-5-sonnet-20241022"

    # Google models
    elif os.getenv("GOOGLE_API_KEY"):
        return "google:gemini-1.5-pro"

    # DeepSeek models
    elif os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek:deepseek-chat"

    # Fireworks models
    elif os.getenv("FIREWORKS_API_KEY"):
        return "fireworks:accounts/fireworks/models/llama-v3p2-3b-instruct"

    # Cohere models
    elif os.getenv("COHERE_API_KEY"):
        return "cohere:command-r-plus"

    # Mistral models
    elif os.getenv("MISTRAL_API_KEY"):
        return "mistral:mistral-large-latest"

    # Groq models
    elif os.getenv("GROQ_API_KEY"):
        return "groq:llama-3.1-70b-versatile"

    # Replicate models
    elif os.getenv("REPLICATE_API_TOKEN"):
        return "replicate:meta/llama-2-70b-chat"

    # Hugging Face models
    elif os.getenv("HUGGINGFACE_API_KEY"):
        return "huggingface:microsoft/DialoGPT-large"

    # AWS Bedrock models
    elif os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        return "aws:anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Azure OpenAI models
    elif os.getenv("AZURE_OPENAI_API_KEY"):
        return "azure:gpt-4o"

    # Default fallback
    else:
        return "openai:gpt-4o-mini"


def _fetch_content_from_urls(search_results: list) -> list:
    """
    Fetch content from URLs asynchronously.

    Args:
        search_results: List of search results with URLs

    Returns:
        List of results with fetched content
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    import aiohttp
    from bs4 import BeautifulSoup

    async def fetch_snippet_async(session, url, title):
        """Fetch page content asynchronously"""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                # crude text extraction: first 2 paragraphs
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                snippet = " ".join(paragraphs[:2])  # Limit to first 2 paragraphs
                return {
                    "title": title,
                    "url": url,
                    "snippet": (
                        snippet[:500] + "..." if len(snippet) > 500 else snippet
                    ),  # Limit snippet length
                }
        except Exception as e:
            return {"title": title, "url": url, "snippet": f"Error fetching page: {e}"}

    async def process_all_urls():
        """Process all URLs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for r in search_results:
                url = r.get("href")
                title = r.get("title", "No title")
                if url:
                    task = fetch_snippet_async(session, url, title)
                    tasks.append(task)
                else:
                    # Handle results without URLs
                    def create_no_url_result(result_title):
                        async def no_url_result():
                            return {
                                "title": result_title,
                                "url": "",
                                "snippet": "No URL available",
                            }

                        return no_url_result

                    tasks.append(create_no_url_result(title)())

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(
                        {
                            "title": "Error",
                            "url": "",
                            "snippet": f"Error processing result: {result}",
                        }
                    )
                else:
                    processed_results.append(result)

            return processed_results

    # Run the async function in a thread pool to avoid blocking
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(process_all_urls())
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        results = executor.submit(run_async).result()

    return results


def _filter_search_results(results: list, exclude_urls: list) -> list:
    """
    Filter out excluded URLs from search results.

    Args:
        results: List of search results from DuckDuckGo
        exclude_urls: List of URLs to exclude

    Returns:
        List of filtered results
    """
    filtered_results = []
    for result in results:
        url = result.get("href", "")
        if url not in exclude_urls:
            filtered_results.append(result)
        else:
            print(f"[TOOL] Excluding URL: {url}")
    return filtered_results


def _get_additional_results(
    rewritten_query: str, exclude_urls: list, existing_results: list
) -> list:
    """
    Get additional search results when initial results are insufficient.

    Args:
        rewritten_query: The rewritten search query
        exclude_urls: List of URLs to exclude
        existing_results: Already found results

    Returns:
        List of additional results
    """
    try:
        from ddgs import DDGS

        ddg = DDGS()

        # Use the same rewritten query but with more results
        additional_results = list(ddg.text(rewritten_query, max_results=15))

        # Add unique results that aren't in exclude_urls or existing_results
        existing_urls = {r.get("href", "") for r in existing_results}
        for result in additional_results:
            url = result.get("href", "")
            if url not in exclude_urls and url not in existing_urls:
                existing_results.append(result)
                if len(existing_results) >= 5:
                    break

    except Exception as e:
        print(f"[TOOL] Failed to get additional results: {e}")

    return existing_results


def _fetch_search_results(rewritten_query: str, exclude_urls: list) -> list:
    """
    Fetch and filter search results from DuckDuckGo.

    Args:
        rewritten_query: The rewritten search query
        exclude_urls: List of URLs to exclude

    Returns:
        List of filtered search results
    """
    from ddgs import DDGS

    ddg = DDGS()

    # Get more results initially to account for filtering
    initial_results = list(ddg.text(rewritten_query, max_results=10))

    # Filter out excluded URLs
    search_results = _filter_search_results(initial_results, exclude_urls)

    # If we don't have enough results after filtering, try to get more
    if len(search_results) < 5:
        print(
            f"[TOOL] Only {len(search_results)} results after filtering, "
            "fetching more..."
        )
        search_results = _get_additional_results(
            rewritten_query, exclude_urls, search_results
        )

    print(f"[TOOL] Final search results count: {len(search_results)}")
    return search_results


def query_rewriter(query: str) -> str:
    """Rewrite query for better search results, with fallback to original query."""
    try:
        from agenthub.core.llm.llm_service import get_shared_llm_service

        llm_service = get_shared_llm_service()
        config = get_config()
        model_name = _load_model_name()
        print(f"[TOOL] Using model: {model_name}")

        prompt = f"""
DDGS search operators

Query example	Result
cats dogs	Results about cats or dogs
"cats and dogs"	Results for exact term "cats and dogs". If no results are
		found, related results are shown.
cats -dogs	Fewer dogs in results
cats +dogs	More dogs in results
dogs site:example.com	Pages about dogs from example.com
cats -site:example.com	Pages about cats, excluding example.com
intitle:dogs	Page title includes the word "dogs"
inurl:cats	Page url includes the word "cats"
Above is some examples of best practices to write query for search.

This is the query you need to rewrite: {query}
Query must be similar with appropriate suggested operators.
Just return the rewritten query, no other text.
        """

        response = llm_service.generate(
            input_data=prompt,
            temperature=config.llm_temperature,
        )

        # Check if we got a fallback response and return original query instead
        if response == "AISuite not available" or not response.strip():
            print("[TOOL] LLM service unavailable, using original query")
            return query

        return response
    except Exception as e:
        print(f"[TOOL] Query rewriter failed ({e}), using original query")
        return query


@tool(
    name="web_search",
    description="Search the web for a query with AI-powered query rewriting",
)
def web_search(query: str, exclude_urls: list = None) -> dict:
    """
    Search the web for a query using DuckDuckGo with automatic query rewriting.

    Args:
        query (str): The search query.
        exclude_urls (list, optional): List of URLs to exclude from search results.

    Returns:
        dict: Contains the original query, rewritten query, and search results.
    """
    try:
        # Initialize exclude_urls if not provided
        if exclude_urls is None:
            exclude_urls = []

        # Automatically rewrite the query using AI
        rewritten_query = query_rewriter(query)
        print(f"[TOOL] Original query: '{query}'")
        print(f"[TOOL] Rewritten query: '{rewritten_query}'")
        print(f"[TOOL] Excluding URLs: {exclude_urls}")
        print(f"[TOOL] Performing web search for: '{rewritten_query}' (max_results=10)")

        # Fetch and filter search results
        search_results = _fetch_search_results(rewritten_query, exclude_urls)

        # Fetch content from URLs
        results = _fetch_content_from_urls(search_results)

        return {
            "original_query": query,
            "rewritten_query": rewritten_query,
            "excluded_urls": exclude_urls or [],
            "results": results,
        }
    except ImportError:
        return {
            "original_query": query,
            "rewritten_query": query,
            "excluded_urls": exclude_urls or [],
            "error": "DuckDuckGo search not available",
            "message": "Please install 'ddgs' package: pip install duckduckgo-search",  # noqa: E501
        }
    except Exception as e:
        return {
            "original_query": query,
            "rewritten_query": query,
            "excluded_urls": exclude_urls or [],
            "error": "Web search failed",
            "message": f"Search error: {str(e)}",
        }


if __name__ == "__main__":
    print("🔍 AgentHub Search Tool Server - Web Search Focused")
    print("=" * 60)

    # Show available tools
    tools = get_available_tools()
    print("📋 Available search tools:")
    for tool_name in tools:
        print(f"  - {tool_name}")

    print("\n✨ Starting search server with framework run_resources() method...")

    # Use the clean framework-level run_resources() function
    run_resources()
