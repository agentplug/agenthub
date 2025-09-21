"""
Web Scraping Implementation

Provides web content extraction with intelligent parsing, metadata extraction,
and comprehensive error handling.
"""

import time
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.base import CachedTool, SecurityValidator


class WebScraper:
    """Advanced web scraping engine with intelligent parsing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.security_validator = SecurityValidator()
        self.text_extractor = TextExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.link_extractor = LinkExtractor()
        self.image_extractor = ImageExtractor()
    
    def scrape(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape web page with specified options."""
        try:
            # Validate URL
            if not self.security_validator.validate_url(url):
                return {
                    "success": False,
                    "error": "Invalid or unsafe URL",
                    "error_type": "security_error"
                }
            
            # Make request
            response = self._make_request(url, options)
            if not response:
                return {
                    "success": False,
                    "error": "Failed to fetch URL",
                    "error_type": "request_error"
                }
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content based on options
            result = {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.text)
            }
            
            if options.get('extract_text', True):
                result['text'] = self.text_extractor.extract(soup)
            
            if options.get('extract_metadata', True):
                result['metadata'] = self.metadata_extractor.extract(soup)
            
            if options.get('extract_links', False):
                result['links'] = self.link_extractor.extract(soup, url)
            
            if options.get('extract_images', False):
                result['images'] = self.image_extractor.extract(soup, url)
            
            return {
                "success": True,
                "data": result,
                "scraped_at": time.time()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Scraping failed: {e}",
                "error_type": "scraping_error"
            }
    
    def _make_request(self, url: str, options: Dict[str, Any]) -> Optional[requests.Response]:
        """Make HTTP request with proper error handling."""
        try:
            timeout = options.get('timeout', 10)
            follow_redirects = options.get('follow_redirects', True)
            user_agent = options.get('user_agent')
            
            if user_agent:
                headers = {'User-Agent': user_agent}
            else:
                headers = self.session.headers
            
            response = self.session.get(
                url,
                timeout=timeout,
                allow_redirects=follow_redirects,
                headers=headers
            )
            response.raise_for_status()
            return response
        
        except requests.RequestException as e:
            return None


class TextExtractor:
    """Extract clean text content from HTML."""
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract main text content from parsed HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text


class MetadataExtractor:
    """Extract metadata from HTML."""
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive metadata from parsed HTML."""
        metadata = {}
        
        # Basic meta tags
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '').strip()
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            metadata['keywords'] = keywords_tag.get('content', '').strip()
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '').strip()
            if content:
                metadata[f'og_{prop}'] = content
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '').strip()
            if content:
                metadata[f'twitter_{name}'] = content
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            metadata['language'] = html_tag.get('lang', '')
        
        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata['author'] = author_tag.get('content', '').strip()
        
        return metadata


class LinkExtractor:
    """Extract links from HTML."""
    
    def extract(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from parsed HTML."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                links.append({
                    'url': absolute_url,
                    'text': link.get_text().strip(),
                    'title': link.get('title', ''),
                    'rel': link.get('rel', [])
                })
        
        return links


class ImageExtractor:
    """Extract images from HTML."""
    
    def extract(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from parsed HTML."""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src)
                
                images.append({
                    'url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        return images


class SecurityValidator:
    """Security validation for web scraping."""
    
    def __init__(self):
        self.blocked_domains = {
            'localhost',
            '127.0.0.1',
            '0.0.0.0'
        }
        self.blocked_schemes = {'file', 'ftp', 'javascript', 'data'}
    
    def validate_url(self, url: str) -> bool:
        """Validate URL for security."""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme in self.blocked_schemes:
                return False
            
            # Check domain
            if parsed.netloc in self.blocked_domains:
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = ['..', 'javascript:', 'data:']
            for pattern in suspicious_patterns:
                if pattern in url:
                    return False
            
            return True
        
        except Exception:
            return False


@tool(
    name="web_scrape",
    description="Extract content from web pages"
)
def web_scrape(
    url: str,
    extract_text: bool = True,
    extract_links: bool = False,
    extract_images: bool = False,
    extract_metadata: bool = True,
    timeout: int = 10,
    user_agent: str = None,
    follow_redirects: bool = True
) -> Dict[str, Any]:
    """
    Extract structured content from web pages.
    
    Args:
        url: URL to scrape
        extract_text: Extract main text content
        extract_links: Extract hyperlinks
        extract_images: Extract image URLs and metadata
        extract_metadata: Extract page metadata (title, description, etc.)
        timeout: Request timeout in seconds
        user_agent: Custom user agent string
        follow_redirects: Whether to follow redirects
    
    Returns:
        dict: Extracted content with text, links, images, and metadata
    """
    try:
        # Validate inputs
        if not url or not url.strip():
            return {
                "success": False,
                "error": "URL cannot be empty",
                "error_type": "validation_error"
            }
        
        if timeout < 1 or timeout > 60:
            return {
                "success": False,
                "error": "Timeout must be between 1 and 60 seconds",
                "error_type": "validation_error"
            }
        
        # Create scraper
        scraper = WebScraper()
        
        # Scrape content
        result = scraper.scrape(url, {
            'extract_text': extract_text,
            'extract_links': extract_links,
            'extract_images': extract_images,
            'extract_metadata': extract_metadata,
            'timeout': timeout,
            'user_agent': user_agent,
            'follow_redirects': follow_redirects
        })
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "unexpected_error"
        }


@tool(
    name="web_scrape_async",
    description="Extract content from multiple web pages asynchronously"
)
def web_scrape_async(
    urls: List[str],
    extract_text: bool = True,
    extract_metadata: bool = True,
    timeout: int = 10,
    max_concurrent: int = 5
) -> Dict[str, Any]:
    """
    Extract content from multiple web pages asynchronously.
    
    Args:
        urls: List of URLs to scrape
        extract_text: Extract main text content
        extract_metadata: Extract page metadata
        timeout: Request timeout in seconds
        max_concurrent: Maximum concurrent requests
    
    Returns:
        dict: Results from all scraping operations
    """
    try:
        # Use ThreadPoolExecutor to simulate async behavior
        import concurrent.futures
        
        def scrape_single_url(url):
            return web_scrape(
                url=url,
                extract_text=extract_text,
                extract_metadata=extract_metadata,
                timeout=timeout
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [executor.submit(scrape_single_url, url) for url in urls]
            results = [future.result() for future in futures]
        
        return {
            "success": True,
            "urls": urls,
            "results": results,
            "total": len(urls),
            "successful": sum(1 for r in results if r.get("success", False))
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Async scraping failed: {e}",
            "error_type": "async_error"
        }
