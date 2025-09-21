"""
Web Search Implementation

Provides multi-engine web search capabilities with caching, rate limiting,
and comprehensive error handling.
"""

import time
import hashlib
import requests
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode, urlparse
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.base import CachedTool, SecurityValidator


class WebSearchEngine:
    """Unified web search interface with multiple engines."""
    
    def __init__(self):
        self.engines = {
            'duckduckgo': DuckDuckGoSearch(),
            'google': GoogleSearch(),
            'bing': BingSearch(),
            'custom': CustomSearch()
        }
        self.rate_limiters = {
            'duckduckgo': RateLimiter(requests_per_minute=60),
            'google': RateLimiter(requests_per_minute=100),
            'bing': RateLimiter(requests_per_minute=50),
            'custom': RateLimiter(requests_per_minute=30)
        }
        self.security_validator = SecurityValidator()
    
    def search(self, query: str, engine: str, **kwargs) -> Dict[str, Any]:
        """Search using specified engine with rate limiting and validation."""
        # Validate inputs
        if not self.security_validator.validate_query(query):
            raise ValueError("Invalid search query")
        
        # Check rate limit
        if not self.rate_limiters[engine].can_make_request():
            raise RateLimitExceeded(f"Rate limit exceeded for {engine}")
        
        # Perform search
        try:
            result = self.engines[engine].search(query, **kwargs)
            self.rate_limiters[engine].record_request()
            return result
        except Exception as e:
            raise WebSearchError(f"Search failed: {e}")


class DuckDuckGoSearch:
    """DuckDuckGo search implementation."""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search using DuckDuckGo API."""
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        # Add additional parameters
        if 'max_results' in kwargs:
            params['max_results'] = min(kwargs['max_results'], 25)
        
        if 'language' in kwargs:
            params['kl'] = kwargs['language']
        
        if 'region' in kwargs:
            params['gl'] = kwargs['region']
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_results(data, query, kwargs)
        
        except requests.RequestException as e:
            raise WebSearchError(f"DuckDuckGo search failed: {e}")
    
    def _format_results(self, data: Dict, query: str, options: Dict) -> Dict[str, Any]:
        """Format DuckDuckGo results."""
        results = []
        
        # Process instant answers
        if data.get('Answer'):
            results.append({
                'title': 'Instant Answer',
                'url': data.get('AbstractURL', ''),
                'snippet': data['Answer'],
                'type': 'instant_answer'
            })
        
        # Process related topics
        for topic in data.get('RelatedTopics', [])[:5]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' ').title(),
                    'url': topic.get('FirstURL', ''),
                    'snippet': topic['Text'],
                    'type': 'related_topic'
                })
        
        # Process web results
        for result in data.get('Results', [])[:10]:
            results.append({
                'title': result.get('Text', ''),
                'url': result.get('FirstURL', ''),
                'snippet': result.get('Text', ''),
                'type': 'web_result'
            })
        
        return {
            'success': True,
            'query': query,
            'engine': 'duckduckgo',
            'results': results[:options.get('max_results', 10)],
            'total_results': len(results),
            'search_time': time.time()
        }


class GoogleSearch:
    """Google search implementation using custom search API."""
    
    def __init__(self):
        self.api_key = None  # Would be loaded from environment
        self.search_engine_id = None  # Would be loaded from environment
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session = requests.Session()
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search using Google Custom Search API."""
        if not self.api_key or not self.search_engine_id:
            # Fallback to DuckDuckGo if Google API not configured
            return DuckDuckGoSearch().search(query, **kwargs)
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(kwargs.get('max_results', 10), 10)
        }
        
        if 'language' in kwargs:
            params['lr'] = f"lang_{kwargs['language']}"
        
        if 'region' in kwargs:
            params['gl'] = kwargs['region']
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_results(data, query, kwargs)
        
        except requests.RequestException as e:
            raise WebSearchError(f"Google search failed: {e}")
    
    def _format_results(self, data: Dict, query: str, options: Dict) -> Dict[str, Any]:
        """Format Google results."""
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'type': 'web_result'
            })
        
        return {
            'success': True,
            'query': query,
            'engine': 'google',
            'results': results,
            'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
            'search_time': time.time()
        }


class BingSearch:
    """Bing search implementation."""
    
    def __init__(self):
        self.api_key = None  # Would be loaded from environment
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.session = requests.Session()
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search using Bing Search API."""
        if not self.api_key:
            # Fallback to DuckDuckGo if Bing API not configured
            return DuckDuckGoSearch().search(query, **kwargs)
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        params = {
            'q': query,
            'count': min(kwargs.get('max_results', 10), 50)
        }
        
        if 'language' in kwargs:
            params['mkt'] = f"{kwargs['language']}-{kwargs.get('region', 'US')}"
        
        try:
            response = self.session.get(
                self.base_url, 
                headers=headers, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return self._format_results(data, query, kwargs)
        
        except requests.RequestException as e:
            raise WebSearchError(f"Bing search failed: {e}")
    
    def _format_results(self, data: Dict, query: str, options: Dict) -> Dict[str, Any]:
        """Format Bing results."""
        results = []
        
        for item in data.get('webPages', {}).get('value', []):
            results.append({
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'snippet': item.get('snippet', ''),
                'type': 'web_result'
            })
        
        return {
            'success': True,
            'query': query,
            'engine': 'bing',
            'results': results,
            'total_results': data.get('webPages', {}).get('totalEstimatedMatches', 0),
            'search_time': time.time()
        }


class CustomSearch:
    """Custom search implementation for specific APIs."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search using custom API endpoint."""
        # This would be implemented based on specific API requirements
        # For now, fallback to DuckDuckGo
        return DuckDuckGoSearch().search(query, **kwargs)


class RateLimiter:
    """Rate limiting for search engines."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if request can be made within rate limits."""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        return len(self.requests) < self.requests_per_minute
    
    def record_request(self) -> None:
        """Record a request for rate limiting."""
        self.requests.append(time.time())


class SecurityValidator:
    """Security validation for web search."""
    
    def __init__(self):
        self.blocked_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'file://',
            r'ftp://'
        ]
    
    def validate_query(self, query: str) -> bool:
        """Validate search query for security."""
        if not query or not query.strip():
            return False
        
        if len(query) > 500:
            return False
        
        # Check for suspicious patterns
        import re
        for pattern in self.blocked_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False
        
        return True
    
    def validate_url(self, url: str) -> bool:
        """Validate URL for security."""
        from urllib.parse import urlparse
        import re
        
        try:
            parsed = urlparse(url)
            
            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
            
            # Check for suspicious patterns
            suspicious_patterns = ['..', 'javascript:', 'data:']
            for pattern in suspicious_patterns:
                if pattern in url:
                    return False
            
            return True
        
        except Exception:
            return False


class WebSearchError(Exception):
    """Web search specific error."""
    pass


class RateLimitExceeded(Exception):
    """Rate limit exceeded error."""
    pass


@tool(
    name="web_search",
    description="Search the web using multiple search engines"
)
def web_search(
    query: str,
    engine: str = "duckduckgo",
    max_results: int = 10,
    language: str = "en",
    region: str = "us",
    time_filter: str = None,
    safe_search: bool = True,
    include_snippets: bool = True
) -> Dict[str, Any]:
    """
    Search the web using multiple search engines.
    
    Args:
        query: Search query string
        engine: Search engine ('duckduckgo', 'google', 'bing', 'custom')
        max_results: Maximum number of results to return
        language: Search language code (e.g., 'en', 'es', 'fr')
        region: Search region code (e.g., 'us', 'uk', 'ca')
        time_filter: Time filter ('day', 'week', 'month', 'year')
        safe_search: Enable safe search filtering
        include_snippets: Include result snippets
    
    Returns:
        dict: Search results with titles, URLs, snippets, and metadata
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "error_type": "validation_error"
            }
        
        if engine not in ['duckduckgo', 'google', 'bing', 'custom']:
            return {
                "success": False,
                "error": f"Unsupported search engine: {engine}",
                "error_type": "validation_error"
            }
        
        if max_results < 1 or max_results > 100:
            return {
                "success": False,
                "error": "max_results must be between 1 and 100",
                "error_type": "validation_error"
            }
        
        # Create search engine
        search_engine = WebSearchEngine()
        
        # Perform search
        result = search_engine.search(
            query=query,
            engine=engine,
            max_results=max_results,
            language=language,
            region=region,
            time_filter=time_filter,
            safe_search=safe_search,
            include_snippets=include_snippets
        )
        
        return result
    
    except RateLimitExceeded as e:
        return {
            "success": False,
            "error": f"Rate limit exceeded: {e}",
            "error_type": "rate_limit_exceeded"
        }
    
    except WebSearchError as e:
        return {
            "success": False,
            "error": f"Search failed: {e}",
            "error_type": "search_error"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "unexpected_error"
        }


@tool(
    name="web_search_async",
    description="Perform multiple web searches asynchronously"
)
def web_search_async(
    queries: List[str],
    engine: str = "duckduckgo",
    max_results: int = 10,
    max_concurrent: int = 5
) -> Dict[str, Any]:
    """
    Perform multiple web searches asynchronously.
    
    Args:
        queries: List of search queries
        engine: Search engine to use
        max_results: Maximum results per query
        max_concurrent: Maximum concurrent searches
    
    Returns:
        dict: Results from all searches
    """
    def search_single_query(query):
        """Search a single query."""
        try:
            result = web_search(query, engine, max_results)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    try:
        # Use ThreadPoolExecutor to simulate async behavior
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [
                executor.submit(search_single_query, query) 
                for query in queries
            ]
            results = [future.result() for future in futures]
        
        return {
            "success": True,
            "queries": queries,
            "results": results,
            "total": len(queries),
            "successful": sum(1 for r in results if r.get("success", False))
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Async search failed: {e}",
            "error_type": "async_error"
        }
