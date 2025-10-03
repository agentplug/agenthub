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


def _extract_pdf_text(pdf_content: bytes, title: str, url: str) -> dict:
    """
    Extract text from PDF content.

    Args:
        pdf_content: PDF file content as bytes
        title: Document title
        url: Document URL

    Returns:
        Dictionary with extracted text and metadata
    """
    try:
        import io

        from pypdf import PdfReader

        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text_content = ""

        # Extract text from all pages
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            text_content += page_text + "\n"

        # Create snippet from first 1000 characters
        snippet = (
            text_content[:1000] + "..." if len(text_content) > 1000 else text_content
        )

        return {
            "title": title,
            "url": url,
            "content": text_content,
            "snippet": snippet,
            "file_type": "PDF",
            "pages": len(pdf_reader.pages),
        }
    except ImportError:
        error_msg = "PDF file detected but PyPDF2 not available. Install with: pip install PyPDF2"  # noqa: E501
        return {
            "title": title,
            "url": url,
            "content": error_msg,
            "snippet": error_msg,
            "file_type": "PDF",
        }
    except Exception as pdf_error:
        error_msg = f"Error extracting PDF text: {pdf_error}"
        return {
            "title": title,
            "url": url,
            "content": error_msg,
            "snippet": error_msg,
            "file_type": "PDF",
        }


def _extract_html_text(html: str, title: str, url: str) -> dict:
    """
    Extract text from HTML content with improved text extraction.

    Args:
        html: HTML content as string
        title: Page title
        url: Page URL

    Returns:
        Dictionary with extracted text
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.decompose()

    # Try multiple extraction strategies
    text_content = ""

    # Strategy 1: Look for main content areas
    main_content = (
        soup.find("main") or soup.find("article") or soup.find("div", class_="content")
    )
    if main_content:
        text_content = main_content.get_text(separator=" ", strip=True)

    # Strategy 2: If no main content, try paragraphs
    if not text_content or len(text_content.strip()) < 50:
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        text_content = " ".join(paragraphs)

    # Strategy 3: If still no content, try divs with text
    if not text_content or len(text_content.strip()) < 50:
        divs = [
            div.get_text(strip=True)
            for div in soup.find_all("div")
            if div.get_text(strip=True)
        ]
        text_content = " ".join(divs[:5])  # Take first 5 divs

    # Strategy 4: Last resort - get all text
    if not text_content or len(text_content.strip()) < 50:
        text_content = soup.get_text(separator=" ", strip=True)

    # Clean up the text
    text_content = " ".join(text_content.split())  # Remove extra whitespace

    # Create snippet from first 500 characters
    snippet = text_content[:500] + "..." if len(text_content) > 500 else text_content

    return {
        "title": title,
        "url": url,
        "content": text_content,
        "snippet": snippet,
    }


def _filter_empty_content(results: list) -> list:
    """
    Filter out results with empty or minimal content.

    Args:
        results: List of results with content

    Returns:
        List of results with meaningful content
    """
    filtered_results = []
    for result in results:
        content = result.get("content", "")
        snippet = result.get("snippet", "")

        # Keep results that have meaningful content
        if (content and len(content.strip()) > 50) or (
            snippet and len(snippet.strip()) > 20
        ):
            filtered_results.append(result)
        else:
            print(
                f"[TOOL] Filtering out result with empty content: "
                f"{result.get('title', 'No title')}"
            )

    return filtered_results


def _fetch_content_from_urls(search_results: list) -> list:
    """
    Fetch content from URLs asynchronously with proper event loop handling.

    Args:
        search_results: List of search results with URLs

    Returns:
        List of results with fetched content
    """
    import asyncio

    import aiohttp

    async def fetch_snippet_async(session, url, title):
        """Fetch page content asynchronously"""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                content_type = response.headers.get("content-type", "").lower()

                # Check if it's a PDF file
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    print(f"[TOOL] Processing PDF file: {title}")
                    # Get PDF content as bytes
                    pdf_content = await response.read()
                    return _extract_pdf_text(pdf_content, title, url)
                else:
                    # Handle regular HTML content
                    html = await response.text()
                    return _extract_html_text(html, title, url)
        except Exception as e:
            error_msg = f"Error fetching page: {e}"
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
            }

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
                            no_url_msg = "No URL available"
                            return {
                                "title": result_title,
                                "url": "",
                                "content": no_url_msg,
                                "snippet": no_url_msg,
                            }

                        return no_url_result

                    tasks.append(create_no_url_result(title)())

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    error_msg = f"Error processing result: {result}"
                    processed_results.append(
                        {
                            "title": "Error",
                            "url": "",
                            "content": error_msg,
                            "snippet": error_msg,
                        }
                    )
                else:
                    processed_results.append(result)

            return processed_results

    # Use the current event loop if available, otherwise create a new one
    try:
        # Try to get the current event loop
        asyncio.get_running_loop()
        # If we're in an async context, we need to run in a thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, process_all_urls())
            return future.result()
    except RuntimeError:
        # No event loop running, we can create one
        return asyncio.run(process_all_urls())


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
        additional_results = list(ddg.text(rewritten_query, max_results=20))

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
    Fetch and filter search results from DuckDuckGo to ensure 10 non-empty results.

    Args:
        rewritten_query: The rewritten search query
        exclude_urls: List of URLs to exclude

    Returns:
        List of filtered search results (aiming for 10+ results)
    """
    from ddgs import DDGS

    ddg = DDGS()

    # Get more results initially to account for filtering and empty content
    initial_results = list(ddg.text(rewritten_query, max_results=20))

    # Filter out excluded URLs
    search_results = _filter_search_results(initial_results, exclude_urls)

    # If we don't have enough results after filtering, try to get more
    if len(search_results) < 10:
        print(
            f"[TOOL] Only {len(search_results)} results after filtering, "
            "fetching more to reach 10+ results..."
        )
        search_results = _get_additional_results(
            rewritten_query, exclude_urls, search_results
        )

    # If still not enough, try with a simplified query
    if len(search_results) < 10:
        print("[TOOL] Still not enough results, trying simplified query...")
        words = rewritten_query.split()
        simplified_query = " ".join(words[:5])  # Take first 5 words
        try:
            additional_results = list(ddg.text(simplified_query, max_results=15))
            additional_filtered = _filter_search_results(
                additional_results, exclude_urls
            )

            # Add unique results
            existing_urls = {r.get("href", "") for r in search_results}
            for result in additional_filtered:
                url = result.get("href", "")
                if url not in existing_urls and url not in exclude_urls:
                    search_results.append(result)
                    if (
                        len(search_results) >= 15
                    ):  # Get extra to account for empty content
                        break
        except Exception as e:
            print(f"[TOOL] Simplified query failed: {e}")

    print(f"[TOOL] Final search results count: {len(search_results)}")
    return search_results


def query_rewriter(query: str) -> str:
    """Rewrite query for better search results using DuckDuckGo search operators."""
    try:
        from agenthub.core.llm.llm_service import get_shared_llm_service

        llm_service = get_shared_llm_service()
        config = get_config()
        model_name = _load_model_name()
        print(f"[TOOL] Using model: {model_name}")

        prompt = f"""
You are a search query optimization expert. Rewrite the given query to use
DuckDuckGo search operators for better results.

DuckDuckGo Search Operators:
- "exact phrase" - Search for exact phrase
- term1 term2 - Results about term1 OR term2
- term1 +term2 - Results with both term1 AND term2
- term1 -term2 - Results with term1 but NOT term2
- site:domain.com - Search only within specific domain
- -site:domain.com - Exclude specific domain
- intitle:keyword - Page title contains keyword
- inurl:keyword - URL contains keyword
- filetype:pdf - Search for specific file types (pdf, doc, xls, ppt, html)

Guidelines:
1. Use quotes for exact phrases when important
2. Use + to require important terms
3. Use - to exclude irrelevant terms
4. Use site: for authoritative sources (gov, edu, org)
5. Use intitle: for specific topics
6. Keep the query focused and relevant
7. Don't over-optimize - keep it natural
8. IMPORTANT: If the query contains specific dates, times, or years,
   preserve them exactly in the rewritten query
9. For time-sensitive queries, include the specific time period

Original query: {query}

Rewrite this query using appropriate DuckDuckGo operators. Return only the
optimized query, no explanations.
        """

        response = llm_service.generate(
            input_data=prompt,
            temperature=config.llm_temperature,
        )

        # Check if we got a fallback response and return original query instead
        if response == "AISuite not available" or not response.strip():
            print("[TOOL] LLM service unavailable, using original query")
            return query

        # Clean up the response
        rewritten_query = response.strip().strip('"').strip("'")
        print(f"[TOOL] Query rewritten: '{query}' -> '{rewritten_query}'")
        return rewritten_query

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
        print(f"[TOOL] Excluding URLs: {exclude_urls}")
        print(f"Number of excluded URLs: {len(exclude_urls)}")

        # Automatically rewrite the query using AI
        rewritten_query = query_rewriter(query)
        print(f"[TOOL] Original query: '{query}'")
        print(f"[TOOL] Rewritten query: '{rewritten_query}'")
        print(f"[TOOL] Excluding URLs: {exclude_urls}")
        print(f"[TOOL] Performing web search for: '{rewritten_query}' (max_results=10)")

        # Fetch and filter search results
        search_results = _fetch_search_results(rewritten_query, exclude_urls)

        # Check if we got any search results
        if not search_results:
            return {
                "original_query": query,
                "rewritten_query": rewritten_query,
                "excluded_urls": exclude_urls or [],
                "error": "No search results found",
                "message": "The search query did not return any results. Try using different keywords or a simpler query.",  # noqa: E501
                "results": [],
            }

        # Fetch content from URLs
        results = _fetch_content_from_urls(search_results)

        # Filter out results with empty content
        filtered_results = _filter_empty_content(results)

        # If we don't have enough results with content, try to get more
        if len(filtered_results) < 10 and len(search_results) > len(filtered_results):
            print(
                f"[TOOL] Only {len(filtered_results)} results with content, "
                "trying to get more..."
            )
            # Get more search results and try again
            more_search_results = _fetch_search_results(rewritten_query, exclude_urls)
            if len(more_search_results) > len(search_results):
                additional_results = _fetch_content_from_urls(
                    more_search_results[len(search_results) :]
                )
                additional_filtered = _filter_empty_content(additional_results)

                # Add unique results
                existing_urls = {r.get("url", "") for r in filtered_results}
                for result in additional_filtered:
                    if result.get("url", "") not in existing_urls:
                        filtered_results.append(result)
                        if len(filtered_results) >= 10:
                            break

        # Limit to 10 results
        final_results = filtered_results[:10]

        return {
            "original_query": query,
            "rewritten_query": rewritten_query,
            "excluded_urls": exclude_urls or [],
            "results": final_results,
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
