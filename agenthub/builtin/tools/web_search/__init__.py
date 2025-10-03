"""
Web Search Builtin Tool Module

Provides web search capabilities with AI-powered query rewriting,
content extraction, and intelligent result filtering.

Usage:
    from agenthub.builtin.tools.web_search import WebSearchTool
    from agenthub.core.tools import tool, run_resources

    # Basic usage
    @tool("web_search", "Search the web")
    def web_search_tool(query: str, exclude_urls: list = None) -> dict:
        return WebSearchTool().search(query, exclude_urls)

    # Advanced usage with custom configuration
    from agenthub.builtin.tools.web_search import WebSearchConfig

    config = WebSearchConfig(max_results=20, enable_query_rewriting=True)

    @tool("web_search", "Search the web")
    def web_search_tool(query: str, exclude_urls: list = None) -> dict:
        return WebSearchTool(config=config).search(query, exclude_urls)

    run_resources()
"""

from .config import WebSearchConfig
from .core import WebSearchTool

__all__ = ["WebSearchTool", "WebSearchConfig"]
