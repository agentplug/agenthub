"""
Web Search and Scrape Tool

Combines web search and scraping functionality for comprehensive
web content retrieval and analysis.
"""

import time
from typing import Dict, List, Any, Optional
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.web.search import web_search
from agenthub.core.tools.builtin.web.scrape import web_scrape


@tool(
    name="web_search_and_scrape",
    description="Search the web and scrape content from results"
)
def web_search_and_scrape(
    query: str,
    max_results: int = 5,
    scrape_content: bool = True,
    engine: str = "duckduckgo",
    timeout: int = 10,
    extract_text: bool = True,
    extract_metadata: bool = True,
    extract_links: bool = False,
    extract_images: bool = False
) -> Dict[str, Any]:
    """
    Search the web and scrape content from top results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to scrape
        scrape_content: Whether to scrape full content from results
        engine: Search engine to use
        timeout: Scraping timeout per URL
        extract_text: Extract main text content
        extract_metadata: Extract page metadata
        extract_links: Extract hyperlinks
        extract_images: Extract image URLs and metadata
    
    Returns:
        dict: Search results with scraped content
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "error_type": "validation_error"
            }
        
        if max_results < 1 or max_results > 20:
            return {
                "success": False,
                "error": "max_results must be between 1 and 20",
                "error_type": "validation_error"
            }
        
        # Step 1: Search the web
        search_result = web_search(
            query=query,
            engine=engine,
            max_results=max_results * 2  # Get more results than needed
        )
        
        if not search_result.get('success', False):
            return {
                "success": False,
                "error": f"Search failed: {search_result.get('error', 'Unknown error')}",
                "error_type": "search_error"
            }
        
        search_results = search_result.get('results', [])
        if not search_results:
            return {
                "success": True,
                "query": query,
                "engine": engine,
                "search_results": [],
                "scraped_content": [],
                "total_found": 0,
                "total_scraped": 0,
                "scrape_success_rate": 0.0
            }
        
        # Step 2: Scrape content from top results
        scraped_content = []
        successful_scrapes = 0
        
        for i, result in enumerate(search_results[:max_results]):
            if not scrape_content:
                # Just return search results without scraping
                scraped_content.append({
                    "search_result": result,
                    "scraped": False
                })
                continue
            
            url = result.get('url', '')
            if not url:
                continue
            
            # Scrape the URL
            scrape_result = web_scrape(
                url=url,
                extract_text=extract_text,
                extract_metadata=extract_metadata,
                extract_links=extract_links,
                extract_images=extract_images,
                timeout=timeout
            )
            
            if scrape_result.get('success', False):
                successful_scrapes += 1
                scraped_content.append({
                    "search_result": result,
                    "scraped": True,
                    "scraped_data": scrape_result.get('data', {}),
                    "scrape_metadata": {
                        "scraped_at": scrape_result.get('scraped_at'),
                        "status_code": scrape_result.get('data', {}).get('status_code'),
                        "content_length": scrape_result.get('data', {}).get('content_length', 0)
                    }
                })
            else:
                scraped_content.append({
                    "search_result": result,
                    "scraped": False,
                    "scrape_error": scrape_result.get('error', 'Unknown scraping error')
                })
        
        return {
            "success": True,
            "query": query,
            "engine": engine,
            "search_results": search_results,
            "scraped_content": scraped_content,
            "total_found": len(search_results),
            "total_scraped": successful_scrapes,
            "scrape_success_rate": successful_scrapes / len(search_results) if search_results else 0,
            "processed_at": time.time()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Search and scrape failed: {e}",
            "error_type": "unexpected_error"
        }
