"""
Async URL fetching and content retrieval
"""

import asyncio
import concurrent.futures
from typing import Any

from .extractors import ContentExtractor


class ContentFetcher:
    """Handles async content fetching from URLs"""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.content_extractor = ContentExtractor()

    def fetch_content_from_urls(
        self, search_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Fetch content from URLs asynchronously with proper event loop handling.

        Args:
            search_results: List of search results with URLs

        Returns:
            List of results with fetched content
        """
        # Use the current event loop if available, otherwise create a new one
        try:
            # Try to get the current event loop
            asyncio.get_running_loop()
            # If we're in an async context, we need to run in a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self._process_all_urls(search_results)
                )
                return future.result()
        except RuntimeError:
            # No event loop running, we can create one
            return asyncio.run(self._process_all_urls(search_results))

    async def _process_all_urls(
        self, search_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process all URLs concurrently"""
        try:
            import aiohttp
        except ImportError:
            # Fallback to synchronous processing if aiohttp not available
            print("[TOOL] aiohttp not available, using synchronous fetching")
            return self._fetch_content_sync(search_results)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for r in search_results:
                url = r.get("href")
                title = r.get("title", "No title")
                if url:
                    task = self._fetch_snippet_async(session, url, title)
                    tasks.append(task)
                else:
                    # Handle results without URLs
                    tasks.append(self._create_no_url_result(title))

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            processed_results: list[dict[str, Any]] = []
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
                elif isinstance(result, dict):
                    processed_results.append(result)

            return processed_results

    async def _fetch_snippet_async(
        self, session: Any, url: str, title: str
    ) -> dict[str, Any]:
        """Fetch page content asynchronously"""
        try:
            import aiohttp

            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                content_type = response.headers.get("content-type", "").lower()

                # Check if it's a PDF file
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    print(f"[TOOL] Processing PDF file: {title}")
                    # Get PDF content as bytes
                    pdf_content = await response.read()
                    return self.content_extractor.extract_content(
                        pdf_content, content_type, title, url
                    )
                else:
                    # Handle regular HTML content
                    html_content = await response.read()
                    return self.content_extractor.extract_content(
                        html_content, content_type, title, url
                    )
        except Exception as e:
            error_msg = f"Error fetching page: {e}"
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
            }

    async def _create_no_url_result(self, title: str) -> dict[str, str]:
        """Create result for entries without URLs"""
        no_url_msg = "No URL available"
        return {
            "title": title,
            "url": "",
            "content": no_url_msg,
            "snippet": no_url_msg,
        }

    def _fetch_content_sync(
        self, search_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Fallback synchronous content fetching"""
        results = []
        for r in search_results:
            url = r.get("href")
            title = r.get("title", "No title")
            if url:
                try:
                    import requests  # type: ignore[import-untyped]

                    response = requests.get(url, timeout=self.config.timeout)
                    content_type = response.headers.get("content-type", "").lower()
                    content = response.content
                    result = self.content_extractor.extract_content(
                        content, content_type, title, url
                    )
                    results.append(result)
                except Exception as e:
                    error_msg = f"Error fetching page: {e}"
                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "content": error_msg,
                            "snippet": error_msg,
                        }
                    )
            else:
                no_url_msg = "No URL available"
                results.append(
                    {
                        "title": title,
                        "url": "",
                        "content": no_url_msg,
                        "snippet": no_url_msg,
                    }
                )
        return results
