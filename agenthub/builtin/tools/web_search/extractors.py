"""
Content extraction utilities for different file types
"""

import io
from typing import Any


class PDFExtractor:
    """Extract text content from PDF files"""

    def extract(self, pdf_content: bytes, title: str, url: str) -> dict[str, Any]:
        """
        Extract text from PDF content.

        Args:
            pdf_content: PDF file content as bytes
            title: Document title
            url: Document URL

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            from pypdf import PdfReader

            pdf_reader = PdfReader(io.BytesIO(pdf_content))
            text_content = ""

            # Extract text from all pages
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                text_content += page_text + "\n"

            # Create snippet from first 1000 characters
            snippet = (
                text_content[:1000] + "..."
                if len(text_content) > 1000
                else text_content
            )

            return {
                "title": title,
                "url": url,
                "content": text_content,
                "snippet": snippet,
                "file_type": "PDF",
                "pages": len(pdf_reader.pages),
            }
        except ImportError:
            error_msg = (
                "PDF file detected but pypdf not available. "
                "Install with: pip install pypdf"
            )
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
                "file_type": "PDF",
            }
        except Exception as pdf_error:
            error_msg = f"Error extracting PDF text: {pdf_error}"
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
                "file_type": "PDF",
            }


class HTMLExtractor:
    """Extract text content from HTML files"""

    def extract(self, html: str, title: str, url: str) -> dict[str, Any]:
        """
        Extract text from HTML content with improved text extraction.

        Args:
            html: HTML content as string
            title: Page title
            url: Page URL

        Returns:
            Dictionary with extracted text
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()

            # Try multiple extraction strategies
            text_content = ""

            # Strategy 1: Look for main content areas
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_="content")
            )
            if main_content:
                text_content = main_content.get_text(separator=" ", strip=True)

            # Strategy 2: If no main content, try paragraphs
            if not text_content or len(text_content.strip()) < 50:
                paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
                text_content = " ".join(paragraphs)

            # Strategy 3: If still no content, try divs with text
            if not text_content or len(text_content.strip()) < 50:
                divs = [
                    div.get_text(strip=True)
                    for div in soup.find_all("div")
                    if div.get_text(strip=True)
                ]
                text_content = " ".join(divs[:5])  # Take first 5 divs

            # Strategy 4: Last resort - get all text
            if not text_content or len(text_content.strip()) < 50:
                text_content = soup.get_text(separator=" ", strip=True)

            # Clean up the text
            text_content = " ".join(text_content.split())  # Remove extra whitespace

            # Create snippet from first 500 characters
            snippet = (
                text_content[:500] + "..." if len(text_content) > 500 else text_content
            )

            return {
                "title": title,
                "url": url,
                "content": text_content,
                "snippet": snippet,
            }
        except ImportError:
            error_msg = (
                "HTML parsing requires beautifulsoup4. "
                "Install with: pip install beautifulsoup4"
            )
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
            }
        except Exception as html_error:
            error_msg = f"Error extracting HTML text: {html_error}"
            return {
                "title": title,
                "url": url,
                "content": error_msg,
                "snippet": error_msg,
            }


class ContentExtractor:
    """Handles content extraction from various formats"""

    def __init__(self) -> None:
        self.pdf_extractor = PDFExtractor()
        self.html_extractor = HTMLExtractor()

    def extract_content(
        self, content: bytes, content_type: str, title: str, url: str
    ) -> dict[str, Any]:
        """
        Extract content based on type.

        Args:
            content: Content as bytes
            content_type: MIME type of the content
            title: Document title
            url: Document URL

        Returns:
            Dictionary with extracted content
        """
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            return self.pdf_extractor.extract(content, title, url)
        else:
            # Convert bytes to string for HTML processing
            html_content = content.decode("utf-8", errors="ignore")
            return self.html_extractor.extract(html_content, title, url)
