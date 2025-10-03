# Web Search Builtin Tool

A comprehensive web search tool with AI-powered query rewriting, content extraction, and intelligent result filtering.

## Features

- 🔍 **DuckDuckGo Search Integration**: Privacy-focused web search
- 🤖 **AI-Powered Query Rewriting**: Automatically optimizes queries using LLM
- 📄 **Content Extraction**: Extracts text from HTML and PDF files
- 🎯 **Smart Filtering**: Filters out empty content and excluded URLs
- ⚡ **Async Fetching**: Concurrent content fetching for better performance

## Installation

Required dependencies:
```bash
pip install duckduckgo-search beautifulsoup4 aiohttp pypdf
```

## Basic Usage

```python
from agenthub.builtin.tools.web_search import WebSearchTool
from agenthub.core.tools import tool, run_resources

@tool("web_search", "Search the web")
def web_search_tool(query: str, exclude_urls: list = None) -> dict:
    return WebSearchTool().search(query, exclude_urls)

if __name__ == "__main__":
    run_resources()
```

## Advanced Usage

### Custom Configuration

```python
from agenthub.builtin.tools.web_search import WebSearchTool, WebSearchConfig
from agenthub.core.tools import tool, run_resources

# Create custom configuration
config = WebSearchConfig(
    max_results=20,                    # Return up to 20 results
    timeout=15,                        # 15 second timeout for fetching
    enable_query_rewriting=True,       # Use AI query rewriting
    enable_content_extraction=True,    # Extract full content
    exclude_domains=["spam.com"]       # Exclude specific domains
)

@tool("web_search", "Search the web with custom settings")
def web_search_tool(query: str, exclude_urls: list = None) -> dict:
    tool = WebSearchTool(config=config)
    return tool.search(query, exclude_urls)

if __name__ == "__main__":
    run_resources()
```

### Multiple Search Tools

```python
from agenthub.builtin.tools.web_search import WebSearchTool, WebSearchConfig
from agenthub.core.tools import tool, run_resources

# Fast search with minimal configuration
fast_config = WebSearchConfig(
    max_results=5,
    enable_query_rewriting=False,
    enable_content_extraction=False
)

# Deep search with full configuration
deep_config = WebSearchConfig(
    max_results=20,
    enable_query_rewriting=True,
    enable_content_extraction=True
)

@tool("fast_search", "Quick web search")
def fast_search_tool(query: str) -> dict:
    return WebSearchTool(config=fast_config).search(query)

@tool("deep_search", "Deep web search with content extraction")
def deep_search_tool(query: str, exclude_urls: list = None) -> dict:
    return WebSearchTool(config=deep_config).search(query, exclude_urls)

if __name__ == "__main__":
    run_resources()
```

## API Reference

### WebSearchTool

**Constructor:**
```python
WebSearchTool(config: WebSearchConfig | None = None)
```

**Methods:**

#### `search(query: str, exclude_urls: list | None = None, max_results: int | None = None) -> dict`

Search the web for a query.

**Parameters:**
- `query` (str): The search query
- `exclude_urls` (list, optional): List of URLs to exclude from results
- `max_results` (int, optional): Override config max_results

**Returns:**
```python
{
    "original_query": str,      # Original query
    "rewritten_query": str,     # AI-rewritten query
    "excluded_urls": list,      # URLs that were excluded
    "results": [                # List of search results
        {
            "title": str,
            "url": str,
            "content": str,     # Full extracted content
            "snippet": str      # Short preview
        }
    ]
}
```

#### `rewrite_query(query: str) -> str`

Rewrite a query using AI for better search results.

**Parameters:**
- `query` (str): The original query

**Returns:**
- `str`: The rewritten query

### WebSearchConfig

**Configuration Options:**

```python
@dataclass
class WebSearchConfig:
    max_results: int = 10              # Maximum number of results
    timeout: int = 10                  # Timeout for fetching (seconds)
    max_content_length: int = 5000     # Max content length per result
    exclude_domains: list[str] = []    # Domains to exclude
    enable_query_rewriting: bool = True   # Use AI query rewriting
    enable_content_extraction: bool = True # Extract full content
```

## Examples

See `examples/builtin_tools/web_search_example.py` for a complete working example.

## Dependencies

- `duckduckgo-search` or `ddgs`: DuckDuckGo search API
- `beautifulsoup4`: HTML parsing
- `aiohttp`: Async HTTP requests
- `pypdf`: PDF text extraction
- `agenthub`: Core framework

## Troubleshooting

**Import Error: duckduckgo-search not found**
```bash
pip install duckduckgo-search
```

**Import Error: beautifulsoup4 not found**
```bash
pip install beautifulsoup4
```

**Import Error: aiohttp not found**
```bash
pip install aiohttp
```

**PDF extraction not working**
```bash
pip install pypdf
```

