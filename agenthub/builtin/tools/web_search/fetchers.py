"""
Async URL fetching and content retrieval
"""

import asyncio
import concurrent.futures
import logging
from typing import Any

from .extractors import ContentExtractor

logger = logging.getLogger(__name__)


class ContentFetcher:
    """Handles async content fetching from URLs"""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.content_extractor = ContentExtractor()
        self._active_tasks: list[asyncio.Task] = []

    def cleanup(self) -> None:
        """Clean up any active resources"""
        try:
            # Cancel any active tasks
            for task in self._active_tasks:
                if not task.done():
                    task.cancel()
            self._active_tasks.clear()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

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
                future = executor.submit(self._run_with_timeout, search_results)
                return future.result(timeout=self.config.timeout + 10)
        except RuntimeError:
            # No event loop running, we can create one
            return self._run_with_timeout(search_results)
        except Exception as e:
            logger.warning(f"Error in fetch_content_from_urls: {e}")
            # Fallback to synchronous processing
            return self._fetch_content_sync(search_results)

    def _run_with_timeout(
        self, search_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Run async processing with proper timeout and cleanup"""
        try:
            return asyncio.run(self._process_all_urls(search_results))
        except Exception as e:
            logger.warning(f"Error in _run_with_timeout: {e}")
            return self._fetch_content_sync(search_results)

    async def _process_all_urls(
        self, search_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process all URLs concurrently"""
        try:
            import aiohttp
        except ImportError:
            # Fallback to synchronous processing if aiohttp not available
            logger.warning("aiohttp not available, using synchronous fetching")
            return self._fetch_content_sync(search_results)

        async with aiohttp.ClientSession() as session:
            # Wrap in real Tasks: the timeout path below calls
            # done()/cancel()/result(), which bare coroutines don't have.
            tasks: list[asyncio.Task[dict[str, Any]]] = []
            for r in search_results:
                url = r.get("href")
                title = r.get("title", "No title")
                if url:
                    tasks.append(
                        asyncio.ensure_future(
                            self._fetch_snippet_async(session, url, title)
                        )
                    )
                else:
                    # Handle results without URLs
                    tasks.append(
                        asyncio.ensure_future(self._create_no_url_result(title))
                    )

            # Execute all requests concurrently with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.config.timeout + 5,
                )
            except TimeoutError:
                logger.warning("Timeout occurred during content fetching")
                # Cancel remaining tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                # Return partial results
                results = []
                for task in tasks:
                    try:
                        if task.done() and not task.cancelled():
                            results.append(task.result())
                        else:
                            results.append(
                                {
                                    "title": "Timeout",
                                    "url": "",
                                    "content": "Request timed out",
                                    "snippet": "Request timed out",
                                }
                            )
                    except Exception:
                        results.append(
                            {
                                "title": "Error",
                                "url": "",
                                "content": "Task failed",
                                "snippet": "Task failed",
                            }
                        )

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

            # Set a shorter timeout for individual requests
            timeout = aiohttp.ClientTimeout(total=min(self.config.timeout, 10))

            async with session.get(url, timeout=timeout) as response:
                # Check response status
                if response.status >= 400:
                    return {
                        "title": title,
                        "url": url,
                        "content": f"HTTP {response.status} error",
                        "snippet": f"HTTP {response.status} error",
                    }

                content_type = response.headers.get("content-type", "").lower()

                # Check if it's a PDF file - but validate content first
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    logger.debug(f"Processing PDF file: {title}")
                    # Get PDF content as bytes
                    pdf_content = await response.read()
                    # Validate PDF content before processing
                    if pdf_content.startswith(b"%PDF"):
                        return self.content_extractor.extract_content(
                            pdf_content, content_type, title, url
                        )
                    else:
                        # Not a real PDF, treat as HTML
                        return self.content_extractor.extract_content(
                            pdf_content, "text/html", title, url
                        )
                else:
                    # Handle regular HTML content
                    html_content = await response.read()
                    return self.content_extractor.extract_content(
                        html_content, content_type, title, url
                    )
        except TimeoutError:
            return {
                "title": title,
                "url": url,
                "content": "Request timed out",
                "snippet": "Request timed out",
            }
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
                    import requests

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
