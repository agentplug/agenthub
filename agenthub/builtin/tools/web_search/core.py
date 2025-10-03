"""
Core web search functionality
"""

from typing import Any

from agenthub.config import get_config

from .config import WebSearchConfig
from .extractors import ContentExtractor
from .fetchers import ContentFetcher
from .filters import ResultFilter


class WebSearchTool:
    """Builtin web search tool with AI-powered query rewriting"""

    def __init__(self, config: WebSearchConfig | None = None):
        """
        Initialize the web search tool.

        Args:
            config: Optional configuration for the web search tool
        """
        self.config = config or WebSearchConfig()
        self.content_fetcher = ContentFetcher(self.config)
        self.result_filter = ResultFilter(self.config)
        self.content_extractor = ContentExtractor()

    def search(
        self,
        query: str,
        exclude_urls: list[str] | None = None,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """
        Search the web for a query using DuckDuckGo with automatic query rewriting.

        Args:
            query: The search query
            exclude_urls: List of URLs to exclude from search results
            max_results: Maximum number of results to return (overrides config)

        Returns:
            Dictionary containing the original query, rewritten query,
            and search results
        """
        try:
            # Initialize exclude_urls if not provided
            if exclude_urls is None:
                exclude_urls = []

            # Use max_results from parameter or config
            num_results = max_results or self.config.max_results

            print(f"[TOOL] Excluding URLs: {exclude_urls}")
            print(f"Number of excluded URLs: {len(exclude_urls)}")

            # Automatically rewrite the query using AI if enabled
            if self.config.enable_query_rewriting:
                rewritten_query = self.rewrite_query(query)
            else:
                rewritten_query = query

            print(f"[TOOL] Original query: '{query}'")
            print(f"[TOOL] Rewritten query: '{rewritten_query}'")
            print(f"[TOOL] Excluding URLs: {exclude_urls}")
            print(
                f"[TOOL] Performing web search for: '{rewritten_query}' "
                f"(max_results={num_results})"
            )

            # Fetch and filter search results
            search_results = self._fetch_search_results(
                rewritten_query, exclude_urls, num_results
            )

            # Check if we got any search results
            if not search_results:
                return {
                    "original_query": query,
                    "rewritten_query": rewritten_query,
                    "excluded_urls": exclude_urls or [],
                    "error": "No search results found",
                    "message": (
                        "The search query did not return any results. "
                        "Try using different keywords or a simpler query."
                    ),
                    "results": [],
                }

            # Fetch content from URLs if enabled
            if self.config.enable_content_extraction:
                results = self.content_fetcher.fetch_content_from_urls(search_results)

                # Filter out results with empty content
                filtered_results = self.result_filter.filter_empty_content(results)

                # Limit to requested number of results
                final_results = filtered_results[:num_results]
            else:
                # Just return search results without content extraction
                final_results = search_results[:num_results]

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
                "message": (
                    "Please install 'duckduckgo-search' package: "
                    "pip install duckduckgo-search"
                ),
            }
        except Exception as e:
            return {
                "original_query": query,
                "rewritten_query": query,
                "excluded_urls": exclude_urls or [],
                "error": "Web search failed",
                "message": f"Search error: {str(e)}",
            }

    def rewrite_query(self, query: str) -> str:
        """
        Rewrite query for better search results using DuckDuckGo search operators.

        Args:
            query: The original search query

        Returns:
            The rewritten query
        """
        try:
            from agenthub.core.llm.llm_service import get_shared_llm_service

            llm_service = get_shared_llm_service()
            config = get_config()

            # LLM service automatically detects and uses the best available model
            current_model = llm_service.get_current_model()
            print(f"[TOOL] Using model: {current_model}")

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

    def _fetch_search_results(
        self, rewritten_query: str, exclude_urls: list[str], max_results: int
    ) -> list[dict[str, Any]]:
        """
        Fetch and filter search results from DuckDuckGo.

        Args:
            rewritten_query: The rewritten search query
            exclude_urls: List of URLs to exclude
            max_results: Maximum number of results to fetch

        Returns:
            List of filtered search results
        """

        from ddgs import DDGS

        ddg = DDGS()

        # Get more results initially to account for filtering and empty content
        initial_results = list(ddg.text(rewritten_query, max_results=max_results * 2))

        # Filter out excluded URLs
        search_results = self.result_filter.filter_search_results(
            initial_results, exclude_urls
        )

        print(f"[TOOL] Final search results count: {len(search_results)}")
        return search_results
