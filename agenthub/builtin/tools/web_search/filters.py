"""
Result filtering and validation logic
"""

from typing import Any


class ResultFilter:
    """Filters and validates search results"""

    def __init__(self, config: Any) -> None:
        self.config = config

    def filter_empty_content(
        self, results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
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

    def filter_search_results(
        self, results: list[dict[str, Any]], exclude_urls: list[str]
    ) -> list[dict[str, Any]]:
        """
        Filter out excluded URLs from search results.

        Args:
            results: List of search results from DuckDuckGo
            exclude_urls: List of URLs to exclude

        Returns:
            List of filtered results
        """
        if not exclude_urls:
            return results

        filtered_results = []
        for result in results:
            url = result.get("href", "")
            if url not in exclude_urls:
                filtered_results.append(result)
            else:
                print(f"[TOOL] Excluding URL: {url}")
        return filtered_results
