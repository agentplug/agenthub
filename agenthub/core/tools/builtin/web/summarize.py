"""
Web Content Summarization

Provides AI-powered content summarization for web pages with multiple
summarization strategies and language support.
"""

import time
import requests
from typing import Dict, List, Any, Optional
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.web.scrape import web_scrape


class ContentSummarizer:
    """AI-powered content summarization engine."""
    
    def __init__(self):
        self.summarizer = TransformersSummarizer()
        self.entity_extractor = EntityExtractor()
        self.topic_extractor = TopicExtractor()
        self.key_point_extractor = KeyPointExtractor()
    
    def summarize(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize web page content."""
        try:
            # First, scrape the content
            scrape_result = web_scrape(
                url=url,
                extract_text=True,
                extract_metadata=True,
                timeout=options.get('timeout', 10)
            )
            
            if not scrape_result.get('success', False):
                return {
                    "success": False,
                    "error": f"Failed to scrape content: {scrape_result.get('error', 'Unknown error')}",
                    "error_type": "scraping_error"
                }
            
            content = scrape_result['data']['text']
            metadata = scrape_result['data'].get('metadata', {})
            
            if not content or len(content.strip()) < 100:
                return {
                    "success": False,
                    "error": "Insufficient content to summarize",
                    "error_type": "content_error"
                }
            
            # Use the direct content summarization method
            result = self.summarize_content_directly(content, options, metadata)
            
            # Add URL to the result if successful
            if result.get('success', False):
                result['data']['url'] = url
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Summarization failed: {e}",
                "error_type": "summarization_error"
            }
    
    def summarize_content_directly(self, content: str, options: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Summarize content directly without URL scraping."""
        try:
            # Handle case where content might be a list instead of string
            if isinstance(content, list):
                # Join list elements into a single string
                content = ' '.join(str(item) for item in content if item)
            
            # Ensure content is a string
            if not isinstance(content, str):
                content = str(content)
            
            if not content or len(content.strip()) < 100:
                return {
                    "success": False,
                    "error": "Insufficient content to summarize",
                    "error_type": "content_error"
                }
            
            if metadata is None:
                metadata = {}
            
            # Generate summary
            summary = self.summarizer.summarize(
                content,
                max_length=options.get('max_length', 500),
                style=options.get('style', 'informative')
            )
            
            result = {
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(content) if content else 0,
                "metadata": metadata
            }
            
            # Extract additional insights
            if options.get('include_key_points', True):
                result['key_points'] = self.key_point_extractor.extract(content)
            
            if options.get('extract_entities', False):
                result['entities'] = self.entity_extractor.extract(content)
            
            if options.get('extract_topics', False):
                result['topics'] = self.topic_extractor.extract(content)
            
            return {
                "success": True,
                "data": result,
                "summarized_at": time.time()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Summarization failed: {e}",
                "error_type": "summarization_error"
            }


class TransformersSummarizer:
    """Text summarization using transformers."""
    
    def __init__(self):
        # For now, use a simple extractive summarization
        # In a full implementation, this would use transformers library
        self.model = None
    
    def summarize(self, text: str, max_length: int = 500, style: str = "informative") -> str:
        """Summarize text using transformers model."""
        # Simple extractive summarization for now
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 3:
            return text
        
        # Score sentences based on word frequency
        scored_sentences = self._score_sentences(sentences)
        
        # Select top sentences
        num_sentences = min(max(1, max_length // 50), len(sentences) // 2)
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:num_sentences]
        
        # Sort by original order
        top_sentences.sort(key=lambda x: x[2])
        
        summary = ' '.join([sent[0] for sent in top_sentences])
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
        
        return summary
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[tuple]:
        """Score sentences based on word frequency."""
        # Count word frequencies
        word_freq = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                word = word.strip('.,!?;:"')
                if len(word) > 2:  # Ignore short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        scored = []
        for i, sentence in enumerate(sentences):
            words = sentence.lower().split()
            score = sum(word_freq.get(word.strip('.,!?;:"'), 0) for word in words)
            scored.append((sentence, score, i))
        
        return scored


class EntityExtractor:
    """Extract named entities from text."""
    
    def extract(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        # Simple entity extraction for now
        # In a full implementation, this would use NER models
        entities = []
        
        # Extract potential person names (capitalized words)
        import re
        person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        persons = re.findall(person_pattern, text)
        for person in persons:
            entities.append({
                'text': person,
                'label': 'PERSON',
                'confidence': 0.8
            })
        
        # Extract potential organizations (words with Inc, Corp, Ltd, etc.)
        org_pattern = r'\b[A-Z][a-zA-Z\s]+(?:Inc|Corp|Ltd|LLC|Company|Corporation)\b'
        orgs = re.findall(org_pattern, text)
        for org in orgs:
            entities.append({
                'text': org,
                'label': 'ORG',
                'confidence': 0.7
            })
        
        # Extract potential locations (words that might be places)
        location_pattern = r'\b[A-Z][a-z]+(?:City|Town|State|Country|Nation)\b'
        locations = re.findall(location_pattern, text)
        for location in locations:
            entities.append({
                'text': location,
                'label': 'LOC',
                'confidence': 0.6
            })
        
        return entities


class TopicExtractor:
    """Extract topics and themes from text."""
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract main topics from text."""
        # Simple topic extraction for now
        # In a full implementation, this would use topic modeling
        
        # Count word frequencies
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:"')
            if len(word) > 4:  # Only consider longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words as topics
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [
            {
                'topic': topic,
                'frequency': freq,
                'relevance': min(freq / len(words), 1.0)
            }
            for topic, freq in topics
        ]


class KeyPointExtractor:
    """Extract key points from text."""
    
    def extract(self, text: str) -> List[str]:
        """Extract key points from text."""
        # Simple key point extraction
        sentences = text.split('.')
        
        # Filter sentences that might be key points
        key_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                # Look for sentences that start with important words
                important_starters = [
                    'important', 'key', 'main', 'primary', 'essential',
                    'crucial', 'significant', 'notable', 'remarkable'
                ]
                if any(sentence.lower().startswith(starter) for starter in important_starters):
                    key_points.append(sentence)
                elif sentence.count(',') >= 2:  # Complex sentences might be important
                    key_points.append(sentence)
        
        return key_points[:5]  # Return top 5 key points


def summarize_content_directly(content: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize content directly without scraping from URL."""
    try:
        # Handle case where content might be a list instead of string
        if isinstance(content, list):
            # Join list elements into a single string
            content = ' '.join(str(item) for item in content if item)
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)
        
        if not content or len(content.strip()) < 100:
            return {
                "success": False,
                "error": "Insufficient content to summarize (minimum 100 characters)",
                "error_type": "content_error"
            }
        
        # Create summarizer
        summarizer = ContentSummarizer()
        
        # Summarize content directly
        result = summarizer.summarize_content_directly(content, options)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error summarizing content: {e}",
            "error_type": "summarization_error"
        }


@tool(
    name="web_summarize",
    description="Summarize web content or text using AI"
)
def web_summarize(
    url: str = None,
    content: str = None,
    max_length: int = 500,
    language: str = "en",
    style: str = "informative",
    include_key_points: bool = True,
    extract_entities: bool = False
) -> Dict[str, Any]:
    """
    Extract and summarize web page content or provided text using AI.
    
    Args:
        url: URL to summarize (optional if content is provided)
        content: Direct text content to summarize (optional if url is provided)
        max_length: Maximum summary length in characters
        language: Target language for summary
        style: Summary style ('informative', 'concise', 'detailed')
        include_key_points: Include key points list
        extract_entities: Extract named entities
    
    Returns:
        dict: Summary with key points, entities, and metadata
    """
    try:
        # Handle case where neither URL nor content is provided
        if not url and not content:
            return {
                "success": True,
                "data": {
                    "warning": "No URL or content provided for summarization",
                    "suggestion": "Use web_search() first to find URLs, then call web_summarize() with the URL or content",
                    "summary": "No content available to summarize",
                    "key_points": [],
                    "entities": [],
                    "metadata": {
                        "original_length": 0,
                        "summary_length": 0,
                        "compression_ratio": 0
                    }
                },
                "summarized_at": time.time()
            }
        
        # Handle case where both URL and content are provided
        if url and content:
            return {
                "success": True,
                "data": {
                    "warning": "Both URL and content provided, summarizing content directly",
                    "summary_data": summarize_content_directly(content, {
                        'max_length': max_length,
                        'language': language,
                        'style': style,
                        'include_key_points': include_key_points,
                        'extract_entities': extract_entities
                    }).get('data', {})
                },
                "summarized_at": time.time()
            }
        
        # If content is provided, summarize it directly
        if content:
            return summarize_content_directly(content, {
                'max_length': max_length,
                'language': language,
                'style': style,
                'include_key_points': include_key_points,
                'extract_entities': extract_entities
            })
        
        # Handle empty or invalid URL
        if not url or not url.strip():
            return {
                "success": True,
                "data": {
                    "warning": "Empty or invalid URL provided",
                    "suggestion": "Provide a valid URL or use web_search() first to find URLs",
                    "summary": "No content available to summarize",
                    "key_points": [],
                    "entities": [],
                    "metadata": {
                        "original_length": 0,
                        "summary_length": 0,
                        "compression_ratio": 0
                    }
                },
                "summarized_at": time.time()
            }
        
        if max_length < 50 or max_length > 2000:
            return {
                "success": False,
                "error": "max_length must be between 50 and 2000",
                "error_type": "validation_error"
            }
        
        if style not in ['informative', 'concise', 'detailed']:
            return {
                "success": False,
                "error": "style must be 'informative', 'concise', or 'detailed'",
                "error_type": "validation_error"
            }
        
        # Create summarizer
        summarizer = ContentSummarizer()
        
        # Summarize content
        result = summarizer.summarize(url, {
            'max_length': max_length,
            'language': language,
            'style': style,
            'include_key_points': include_key_points,
            'extract_entities': extract_entities,
            'timeout': 15
        })
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "unexpected_error"
        }
