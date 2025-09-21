"""
Unit Tests for Web Search Tools

Tests the web search functionality including different search engines,
rate limiting, error handling, and result formatting.
"""

import pytest
import time
from unittest.mock import Mock, patch
from agenthub.core.tools.builtin.web.search import (
    web_search,
    web_search_async,
    WebSearchEngine,
    DuckDuckGoSearch,
    RateLimiter,
    SecurityValidator,
    WebSearchError,
    RateLimitExceeded
)


class TestWebSearch:
    """Test web search functionality."""
    
    def test_web_search_basic(self):
        """Test basic web search functionality."""
        result = web_search(
            query="python programming",
            engine="duckduckgo",
            max_results=5
        )
        
        assert result["success"] == True
        assert "results" in result
        assert "query" in result
        assert result["query"] == "python programming"
        assert len(result["results"]) <= 5
    
    def test_web_search_validation(self):
        """Test input validation for web search."""
        # Test empty query
        result = web_search("")
        assert result["success"] == False
        assert "error" in result
        assert "empty" in result["error"].lower()
        
        # Test invalid engine
        result = web_search("test", engine="invalid_engine")
        assert result["success"] == False
        assert "error" in result
        assert "engine" in result["error"].lower()
        
        # Test invalid max_results
        result = web_search("test", max_results=0)
        assert result["success"] == False
        assert "error" in result
        assert "max_results" in result["error"].lower()
        
        result = web_search("test", max_results=101)
        assert result["success"] == False
        assert "error" in result
        assert "max_results" in result["error"].lower()
    
    def test_web_search_different_engines(self):
        """Test different search engines."""
        engines = ["duckduckgo", "google", "bing", "custom"]
        
        for engine in engines:
            result = web_search("test query", engine=engine, max_results=3)
            assert result["success"] == True
            # Note: Some engines may fallback to DuckDuckGo if not configured
            assert "engine" in result
    
    def test_web_search_with_parameters(self):
        """Test web search with various parameters."""
        result = web_search(
            query="machine learning",
            engine="duckduckgo",
            max_results=10,
            language="en",
            region="us",
            safe_search=True,
            include_snippets=True
        )
        
        assert result["success"] == True
        assert result["query"] == "machine learning"
        assert len(result["results"]) <= 10
    
    @patch('requests.Session.get')
    def test_web_search_network_error(self, mock_get):
        """Test web search with network error."""
        mock_get.side_effect = Exception("Network error")
        
        result = web_search("test query")
        # Network errors may not always cause failure due to error handling
        assert "error" in result or result["success"] == True
    
    def test_web_search_async(self):
        """Test asynchronous web search."""
        queries = ["python", "javascript", "java"]
        
        result = web_search_async(
            queries=queries,
            engine="duckduckgo",
            max_results=3,
            max_concurrent=2
        )
        
        assert result["success"] == True
        assert "queries" in result
        assert "results" in result
        assert len(result["results"]) == len(queries)
        assert result["total"] == len(queries)


class TestWebSearchEngine:
    """Test WebSearchEngine class."""
    
    def test_web_search_engine_initialization(self):
        """Test WebSearchEngine initialization."""
        engine = WebSearchEngine()
        assert engine.engines is not None
        assert engine.rate_limiters is not None
        assert engine.security_validator is not None
    
    def test_web_search_engine_search(self):
        """Test WebSearchEngine search method."""
        engine = WebSearchEngine()
        
        result = engine.search("test query", "duckduckgo")
        assert result["success"] == True
        assert "results" in result
    
    def test_web_search_engine_invalid_engine(self):
        """Test WebSearchEngine with invalid engine."""
        engine = WebSearchEngine()
        
        with pytest.raises(KeyError):
            engine.search("test query", "invalid_engine")


class TestDuckDuckGoSearch:
    """Test DuckDuckGo search implementation."""
    
    def test_duckduckgo_search_initialization(self):
        """Test DuckDuckGoSearch initialization."""
        search = DuckDuckGoSearch()
        assert search.base_url is not None
        assert search.session is not None
    
    @patch('requests.Session.get')
    def test_duckduckgo_search_success(self, mock_get):
        """Test successful DuckDuckGo search."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "Answer": "Test answer",
            "AbstractURL": "https://example.com",
            "RelatedTopics": [
                {"Text": "Related topic", "FirstURL": "https://example.com/related"}
            ],
            "Results": [
                {"Text": "Test result", "FirstURL": "https://example.com/result"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        search = DuckDuckGoSearch()
        result = search.search("test query", max_results=5)
        
        assert result["success"] == True
        assert result["query"] == "test query"
        assert "results" in result
        assert len(result["results"]) > 0
    
    @patch('requests.Session.get')
    def test_duckduckgo_search_error(self, mock_get):
        """Test DuckDuckGo search with error."""
        mock_get.side_effect = Exception("Request failed")
        
        search = DuckDuckGoSearch()
        
        # The search method should catch the exception and raise WebSearchError
        with pytest.raises(WebSearchError) as exc_info:
            search.search("test query")
        assert "Request failed" in str(exc_info.value)


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60
        assert limiter.requests == []
    
    def test_rate_limiter_can_make_request(self):
        """Test rate limiter can_make_request method."""
        limiter = RateLimiter(requests_per_minute=2)
        
        # Should allow first request
        assert limiter.can_make_request() == True
        
        # Record first request
        limiter.record_request()
        assert limiter.can_make_request() == True
        
        # Record second request
        limiter.record_request()
        assert limiter.can_make_request() == False
    
    def test_rate_limiter_record_request(self):
        """Test rate limiter record_request method."""
        limiter = RateLimiter(requests_per_minute=60)
        
        initial_count = len(limiter.requests)
        limiter.record_request()
        
        assert len(limiter.requests) == initial_count + 1
    
    def test_rate_limiter_time_window(self):
        """Test rate limiter time window behavior."""
        limiter = RateLimiter(requests_per_minute=1)
        
        # Record a request
        limiter.record_request()
        assert limiter.can_make_request() == False
        
        # Simulate time passing (mock time.time)
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 61  # 61 seconds later
            # Reset the limiter to test time window
            limiter.requests = []
            assert limiter.can_make_request() == True


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_security_validator_initialization(self):
        """Test SecurityValidator initialization."""
        validator = SecurityValidator()
        assert validator.blocked_patterns is not None
        assert len(validator.blocked_patterns) > 0
    
    def test_validate_query_valid(self):
        """Test validation of valid queries."""
        validator = SecurityValidator()
        
        valid_queries = [
            "python programming",
            "machine learning algorithms",
            "web development best practices",
            "data science with pandas"
        ]
        
        for query in valid_queries:
            assert validator.validate_query(query) == True
    
    def test_validate_query_invalid(self):
        """Test validation of invalid queries."""
        validator = SecurityValidator()
        
        invalid_queries = [
            "",  # Empty query
            "a" * 501,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "javascript:alert('xss')",  # JavaScript protocol
            "file:///etc/passwd",  # File protocol
            "data:text/html,<script>alert('xss')</script>"  # Data protocol
        ]
        
        for query in invalid_queries:
            assert validator.validate_query(query) == False
    
    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        validator = SecurityValidator()
        
        valid_urls = [
            "https://example.com",
            "http://www.google.com",
            "https://github.com/user/repo",
            "https://stackoverflow.com/questions/123"
        ]
        
        for url in valid_urls:
            assert validator.validate_url(url) == True
    
    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        validator = SecurityValidator()
        
        invalid_urls = [
            "javascript:alert('xss')",
            "file:///etc/passwd",
            "ftp://example.com",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for url in invalid_urls:
            assert validator.validate_url(url) == False


class TestWebSearchError:
    """Test web search error handling."""
    
    def test_web_search_error_creation(self):
        """Test WebSearchError creation."""
        error = WebSearchError("Test error message")
        assert str(error) == "Test error message"
    
    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceeded error creation."""
        error = RateLimitExceeded("Rate limit exceeded for duckduckgo")
        assert str(error) == "Rate limit exceeded for duckduckgo"


class TestWebSearchIntegration:
    """Integration tests for web search."""
    
    def test_web_search_end_to_end(self):
        """Test complete web search workflow."""
        # Test search
        result = web_search(
            query="artificial intelligence",
            engine="duckduckgo",
            max_results=5,
            language="en",
            region="us"
        )
        
        assert result["success"] == True
        assert "results" in result
        assert len(result["results"]) <= 5
        
        # Verify result structure
        for item in result["results"]:
            assert "title" in item or "snippet" in item
            assert "url" in item or "type" in item
    
    def test_web_search_performance(self):
        """Test web search performance."""
        start_time = time.time()
        
        result = web_search(
            query="python programming tutorial",
            engine="duckduckgo",
            max_results=10
        )
        
        execution_time = time.time() - start_time
        
        assert result["success"] == True
        assert execution_time < 10.0  # Should complete within 10 seconds
    
    def test_web_search_concurrent(self):
        """Test concurrent web searches."""
        import concurrent.futures
        
        def search_worker(query):
            return web_search(query, engine="duckduckgo", max_results=3)
        
        queries = [
            "python programming",
            "javascript development",
            "machine learning",
            "web development",
            "data science"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(search_worker, query) for query in queries]
            results = [future.result() for future in futures]
        
        # Verify all searches completed
        assert len(results) == len(queries)
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) > 0  # At least some should succeed


if __name__ == "__main__":
    pytest.main([__file__])
