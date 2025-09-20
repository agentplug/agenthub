"""Web search tools."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from ...decorator import tool


def _query_rewriter(query: str) -> str:
    """Rewrite query for better search results using AI."""
    try:
        import aisuite as ai
        
        client = ai.Client()
        prompt = """
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
        """.format(query=query)
        
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use a default model
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except ImportError:
        # Fallback to original query if aisuite is not available
        return query
    except Exception:
        # Fallback to original query on any error
        return query


@tool(
    name="web_search",
    description="Search the web for a query and return summarized results",
    version="1.0.0"
)
def web_search(query: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Search the web for a query using DuckDuckGo and return summarized results.

    Args:
        query (str): The search query.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary with 'results' key containing
            a list of dictionaries with 'title', 'url', and 'snippet' for each result.
    """
    try:
        import aiohttp
        from bs4 import BeautifulSoup
        from ddgs import DDGS
    except ImportError as e:
        raise ImportError(
            "Required packages 'ddgs', 'beautifulsoup4', and 'aiohttp' "
            "are not installed."
        ) from e

    # Rewrite query for better results
    optimized_query = _query_rewriter(query)
    
    # Perform search
    ddg = DDGS()
    search_results = list(ddg.text(optimized_query, max_results=5))

    async def fetch_snippet_async(session: aiohttp.ClientSession, url: str, title: str) -> Dict[str, str]:
        """Fetch page content asynchronously"""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                # Extract first 2 paragraphs
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                snippet = " ".join(paragraphs[:2])
                return {
                    "title": title,
                    "url": url,
                    "snippet": (
                        snippet[:500] + "..." if len(snippet) > 500 else snippet
                    ),
                }
        except Exception as e:
            return {
                "title": title,
                "url": url,
                "snippet": f"Error fetching page: {e}"
            }

    async def process_all_urls() -> List[Dict[str, str]]:
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
                    async def no_url_result() -> Dict[str, str]:
                        return {
                            "title": title,
                            "url": "",
                            "snippet": "No URL available",
                        }
                    tasks.append(no_url_result())

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({
                        "title": "Error",
                        "url": "",
                        "snippet": f"Error processing result: {result}",
                    })
                else:
                    processed_results.append(result)

            return processed_results

    # Run the async function in a thread pool to avoid blocking
    def run_async() -> List[Dict[str, str]]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(process_all_urls())
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        results = executor.submit(run_async).result()

    return {"results": results}
