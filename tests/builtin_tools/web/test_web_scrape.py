"""
Unit Tests for Web Scraping Tools

Tests the web scraping functionality including content extraction,
metadata parsing, link extraction, and error handling.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from agenthub.core.tools.builtin.web.scrape import (
    web_scrape,
    web_scrape_async,
    WebScraper,
    TextExtractor,
    MetadataExtractor,
    LinkExtractor,
    ImageExtractor,
    SecurityValidator
)


class TestWebScrape:
    """Test web scraping functionality."""
    
    def test_web_scrape_basic(self):
        """Test basic web scraping functionality."""
        result = web_scrape(
            url="https://httpbin.org/html",
            extract_text=True,
            extract_metadata=True
        )
        
        assert result["success"] == True
        assert "data" in result
        assert "text" in result["data"]
        assert "metadata" in result["data"]
    
    def test_web_scrape_validation(self):
        """Test input validation for web scraping."""
        # Test empty URL
        result = web_scrape("")
        assert result["success"] == False
        assert "error" in result
        assert "empty" in result["error"].lower()
        
        # Test invalid timeout
        result = web_scrape("https://example.com", timeout=0)
        assert result["success"] == False
        assert "error" in result
        assert "timeout" in result["error"].lower()
        
        result = web_scrape("https://example.com", timeout=61)
        assert result["success"] == False
        assert "error" in result
        assert "timeout" in result["error"].lower()
    
    def test_web_scrape_with_options(self):
        """Test web scraping with various options."""
        result = web_scrape(
            url="https://httpbin.org/html",
            extract_text=True,
            extract_links=True,
            extract_images=True,
            extract_metadata=True,
            timeout=15,
            user_agent="Custom Agent",
            follow_redirects=True
        )
        
        assert result["success"] == True
        assert "data" in result
        assert "text" in result["data"]
        assert "metadata" in result["data"]
        assert "links" in result["data"]
        assert "images" in result["data"]
    
    def test_web_scrape_async(self):
        """Test asynchronous web scraping."""
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        result = web_scrape_async(
            urls=urls,
            extract_text=True,
            extract_metadata=True,
            timeout=10,
            max_concurrent=2
        )
        
        assert result["success"] == True
        assert "urls" in result
        assert "results" in result
        assert len(result["results"]) == len(urls)
        assert result["total"] == len(urls)
    
    @patch('requests.Session.get')
    def test_web_scrape_network_error(self, mock_get):
        """Test web scraping with network error."""
        mock_get.side_effect = Exception("Network error")
        
        result = web_scrape("https://example.com")
        assert result["success"] == False
        assert "error" in result
        assert "error_type" in result
    
    def test_web_scrape_invalid_url(self):
        """Test web scraping with invalid URL."""
        result = web_scrape("not-a-url")
        assert result["success"] == False
        assert "error" in result


class TestWebScraper:
    """Test WebScraper class."""
    
    def test_web_scraper_initialization(self):
        """Test WebScraper initialization."""
        scraper = WebScraper()
        assert scraper.session is not None
        assert scraper.security_validator is not None
        assert scraper.text_extractor is not None
        assert scraper.metadata_extractor is not None
        assert scraper.link_extractor is not None
        assert scraper.image_extractor is not None
    
    @patch('requests.Session.get')
    def test_web_scraper_success(self, mock_get):
        """Test successful web scraping."""
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>This is test content.</p>
            <a href="https://example.com">Test Link</a>
            <img src="test.jpg" alt="Test Image">
        </body>
        </html>
        """
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        scraper = WebScraper()
        result = scraper.scrape("https://example.com", {
            'extract_text': True,
            'extract_metadata': True,
            'extract_links': True,
            'extract_images': True,
            'timeout': 10
        })
        
        assert result["success"] == True
        assert "data" in result
        assert "text" in result["data"]
        assert "metadata" in result["data"]
        assert "links" in result["data"]
        assert "images" in result["data"]
    
    def test_web_scraper_invalid_url(self):
        """Test web scraper with invalid URL."""
        scraper = WebScraper()
        result = scraper.scrape("javascript:alert('xss')", {})
        
        assert result["success"] == False
        assert "error" in result
        assert "unsafe" in result["error"].lower()


class TestTextExtractor:
    """Test TextExtractor class."""
    
    def test_text_extractor_initialization(self):
        """Test TextExtractor initialization."""
        extractor = TextExtractor()
        assert extractor is not None
    
    def test_text_extraction(self):
        """Test text extraction from HTML."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph with <strong>bold text</strong>.</p>
            <script>alert('xss');</script>
            <style>body { color: red; }</style>
            <nav>Navigation</nav>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        text = extractor.extract(soup)
        
        assert "Main Heading" in text
        assert "This is a paragraph with bold text" in text
        assert "alert('xss')" not in text  # Script should be removed
        assert "body { color: red; }" not in text  # Style should be removed
        assert "Navigation" not in text  # Nav should be removed


class TestMetadataExtractor:
    """Test MetadataExtractor class."""
    
    def test_metadata_extractor_initialization(self):
        """Test MetadataExtractor initialization."""
        extractor = MetadataExtractor()
        assert extractor is not None
    
    def test_metadata_extraction(self):
        """Test metadata extraction from HTML."""
        from bs4 import BeautifulSoup
        
        html = """
        <html lang="en">
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="Test page description">
            <meta name="keywords" content="test, page, example">
            <meta name="author" content="Test Author">
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta name="twitter:card" content="summary">
            <meta name="twitter:title" content="Twitter Title">
        </head>
        <body>Content</body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        extractor = MetadataExtractor()
        metadata = extractor.extract(soup)
        
        assert metadata['title'] == "Test Page Title"
        assert metadata['description'] == "Test page description"
        assert metadata['keywords'] == "test, page, example"
        assert metadata['author'] == "Test Author"
        assert metadata['language'] == "en"
        assert metadata['og_title'] == "OG Title"
        assert metadata['og_description'] == "OG Description"
        assert metadata['twitter_card'] == "summary"
        assert metadata['twitter_title'] == "Twitter Title"


class TestLinkExtractor:
    """Test LinkExtractor class."""
    
    def test_link_extractor_initialization(self):
        """Test LinkExtractor initialization."""
        extractor = LinkExtractor()
        assert extractor is not None
    
    def test_link_extraction(self):
        """Test link extraction from HTML."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
        <body>
            <a href="https://example.com">Example Link</a>
            <a href="/relative/path" title="Relative Link">Relative</a>
            <a href="https://test.com" rel="nofollow">Test Link</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        extractor = LinkExtractor()
        links = extractor.extract(soup, "https://base.com")
        
        assert len(links) == 3
        
        # Check first link
        assert links[0]['url'] == "https://example.com"
        assert links[0]['text'] == "Example Link"
        
        # Check relative link (should be converted to absolute)
        assert links[1]['url'] == "https://base.com/relative/path"
        assert links[1]['text'] == "Relative"
        assert links[1]['title'] == "Relative Link"
        
        # Check third link
        assert links[2]['url'] == "https://test.com"
        assert links[2]['text'] == "Test Link"
        assert links[2]['rel'] == ["nofollow"]


class TestImageExtractor:
    """Test ImageExtractor class."""
    
    def test_image_extractor_initialization(self):
        """Test ImageExtractor initialization."""
        extractor = ImageExtractor()
        assert extractor is not None
    
    def test_image_extraction(self):
        """Test image extraction from HTML."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
        <body>
            <img src="https://example.com/image1.jpg" alt="Image 1" title="Title 1">
            <img src="/relative/image2.png" alt="Image 2" width="100" height="200">
            <img src="test.gif" alt="Image 3">
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        extractor = ImageExtractor()
        images = extractor.extract(soup, "https://base.com")
        
        assert len(images) == 3
        
        # Check first image
        assert images[0]['url'] == "https://example.com/image1.jpg"
        assert images[0]['alt'] == "Image 1"
        assert images[0]['title'] == "Title 1"
        
        # Check relative image (should be converted to absolute)
        assert images[1]['url'] == "https://base.com/relative/image2.png"
        assert images[1]['alt'] == "Image 2"
        assert images[1]['width'] == "100"
        assert images[1]['height'] == "200"
        
        # Check third image
        assert images[2]['url'] == "https://base.com/test.gif"
        assert images[2]['alt'] == "Image 3"


class TestSecurityValidator:
    """Test security validation for web scraping."""
    
    def test_security_validator_initialization(self):
        """Test SecurityValidator initialization."""
        validator = SecurityValidator()
        assert validator.blocked_domains is not None
        assert validator.blocked_schemes is not None
    
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


class TestWebScrapeIntegration:
    """Integration tests for web scraping."""
    
    def test_web_scrape_end_to_end(self):
        """Test complete web scraping workflow."""
        result = web_scrape(
            url="https://httpbin.org/html",
            extract_text=True,
            extract_metadata=True,
            extract_links=True,
            extract_images=True,
            timeout=10
        )
        
        assert result["success"] == True
        assert "data" in result
        assert "text" in result["data"]
        assert "metadata" in result["data"]
        assert "links" in result["data"]
        assert "images" in result["data"]
    
    def test_web_scrape_performance(self):
        """Test web scraping performance."""
        import time
        
        start_time = time.time()
        
        result = web_scrape(
            url="https://httpbin.org/html",
            extract_text=True,
            extract_metadata=True,
            timeout=5
        )
        
        execution_time = time.time() - start_time
        
        assert result["success"] == True
        assert execution_time < 10.0  # Should complete within 10 seconds
    
    def test_web_scrape_concurrent(self):
        """Test concurrent web scraping."""
        import concurrent.futures
        
        def scrape_worker(url):
            return web_scrape(url, extract_text=True, timeout=5)
        
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(scrape_worker, url) for url in urls]
            results = [future.result() for future in futures]
        
        # Verify all scrapes completed
        assert len(results) == len(urls)
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) > 0  # At least some should succeed


if __name__ == "__main__":
    pytest.main([__file__])
