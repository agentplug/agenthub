from agenthub.builtin.tools.web_search import WebSearchTool
from agenthub.core.tools import run_resources, tool


@tool(
    name="web_search",
    description="Search the web for a query with AI-powered query rewriting",
)
def web_search(query: str, exclude_urls: list[str] | None = None) -> dict:
    return WebSearchTool().search(query, exclude_urls, max_results=10)


run_resources()
