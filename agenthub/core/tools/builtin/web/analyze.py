"""
Web Content Analysis

Provides comprehensive content analysis including sentiment analysis,
topic extraction, and content insights.
"""

import time
import requests
from typing import Dict, List, Any, Optional
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.web.scrape import web_scrape


class ContentAnalyzer:
    """Comprehensive web content analysis engine."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.entity_extractor = EntityExtractor()
        self.readability_analyzer = ReadabilityAnalyzer()
        self.language_detector = LanguageDetector()
    
    def analyze(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze web page content comprehensively."""
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
            
            if not content or len(content.strip()) < 10:
                return {
                    "success": True,
                    "data": {
                        "warning": "Content too short for meaningful analysis",
                        "suggestion": "Provide longer content (at least 10 characters) for better analysis results",
                        "analysis": {
                            "sentiment": "neutral",
                            "topics": [],
                            "keywords": [],
                            "entities": [],
                            "readability_score": 0,
                            "language": "unknown"
                        }
                    },
                    "analyzed_at": time.time()
                }
            
            # Analyze the content
            return self.analyze_content_directly(content, options, metadata)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {e}",
                "error_type": "analysis_error"
            }
    
    def analyze_content_directly(self, content: str, options: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze content directly without URL scraping."""
        try:
            # Handle case where content might be a list instead of string
            if isinstance(content, list):
                # Join list elements into a single string
                content = ' '.join(str(item) for item in content if item)
            
            # Ensure content is a string
            if not isinstance(content, str):
                content = str(content)
            
            if not content or len(content.strip()) < 50:
                return {
                    "success": False,
                    "error": "Insufficient content to analyze",
                    "error_type": "content_error"
                }
            
            if metadata is None:
                metadata = {}
            
            # Perform analysis
            analysis = {
                "content_length": len(content),
                "word_count": len(content.split()),
                "metadata": metadata
            }
            
            # Sentiment analysis
            if options.get('extract_sentiment', True):
                analysis['sentiment'] = self.sentiment_analyzer.analyze(content)
            
            # Topic extraction
            if options.get('extract_topics', True):
                analysis['topics'] = self.topic_extractor.extract(content)
            
            # Keyword extraction
            if options.get('extract_keywords', True):
                analysis['keywords'] = self.keyword_extractor.extract(content)
            
            # Entity extraction
            if options.get('extract_entities', True):
                analysis['entities'] = self.entity_extractor.extract(content)
            
            # Readability analysis
            if options.get('analyze_readability', False):
                analysis['readability'] = self.readability_analyzer.analyze(content)
            
            # Language detection
            if options.get('detect_language', False):
                analysis['language'] = self.language_detector.detect(content)
            
            return {
                "success": True,
                "data": analysis,
                "analyzed_at": time.time()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {e}",
                "error_type": "analysis_error"
            }


class SentimentAnalyzer:
    """Sentiment analysis for text content."""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text content."""
        # Simple sentiment analysis based on word lists
        # In a full implementation, this would use a trained model
        
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'brilliant', 'outstanding', 'perfect', 'love', 'like',
            'enjoy', 'happy', 'pleased', 'satisfied', 'impressed', 'delighted'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
            'dislike', 'angry', 'frustrated', 'disappointed', 'sad', 'upset',
            'annoyed', 'irritated', 'furious', 'outraged', 'disgusted'
        }
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        positive_ratio = positive_count / total_words if total_words > 0 else 0
        negative_ratio = negative_count / total_words if total_words > 0 else 0
        
        # Determine overall sentiment
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            confidence = positive_ratio
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            confidence = negative_ratio
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'positive_words': positive_count,
            'negative_words': negative_count
        }


class TopicExtractor:
    """Extract topics and themes from text."""
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract main topics from text."""
        # Count word frequencies
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            word = word.strip('.,!?;:"()[]{}')
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words as topics
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return [
            {
                'topic': topic,
                'frequency': freq,
                'relevance': min(freq / len(words), 1.0)
            }
            for topic, freq in topics
        ]


class KeywordExtractor:
    """Extract important keywords from text."""
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract keywords from text."""
        # Simple keyword extraction based on frequency and position
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:"()[]{}')
            if len(word) > 2 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score keywords based on frequency and length
        keywords = []
        for word, freq in word_freq.items():
            if freq > 1:  # Only consider words that appear more than once
                score = freq * len(word)  # Longer words get higher scores
                keywords.append({
                    'keyword': word,
                    'frequency': freq,
                    'score': score
                })
        
        # Sort by score and return top keywords
        keywords.sort(key=lambda x: x['score'], reverse=True)
        return keywords[:20]


class EntityExtractor:
    """Extract named entities from text."""
    
    def extract(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        import re
        entities = []
        
        # Extract potential person names (Title Case words)
        person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        persons = re.findall(person_pattern, text)
        for person in set(persons):  # Remove duplicates
            entities.append({
                'text': person,
                'label': 'PERSON',
                'confidence': 0.8
            })
        
        # Extract potential organizations
        org_pattern = r'\b[A-Z][a-zA-Z\s]+(?:Inc|Corp|Ltd|LLC|Company|Corporation|Organization|Association)\b'
        orgs = re.findall(org_pattern, text)
        for org in set(orgs):
            entities.append({
                'text': org,
                'label': 'ORG',
                'confidence': 0.7
            })
        
        # Extract potential locations
        location_pattern = r'\b[A-Z][a-z]+(?:City|Town|State|Country|Nation|Province|Region)\b'
        locations = re.findall(location_pattern, text)
        for location in set(locations):
            entities.append({
                'text': location,
                'label': 'LOC',
                'confidence': 0.6
            })
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in set(emails):
            entities.append({
                'text': email,
                'label': 'EMAIL',
                'confidence': 0.9
            })
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        for url in set(urls):
            entities.append({
                'text': url,
                'label': 'URL',
                'confidence': 0.9
            })
        
        return entities


class ReadabilityAnalyzer:
    """Analyze text readability."""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze readability of text."""
        sentences = text.split('.')
        words = text.split()
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Count complex words (more than 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = complex_words / len(words) if words else 0
        
        # Simple readability score (0-100, higher is easier)
        readability_score = max(0, min(100, 100 - (avg_sentence_length * 2) - (complex_word_ratio * 50)))
        
        # Determine readability level
        if readability_score >= 80:
            level = 'Very Easy'
        elif readability_score >= 60:
            level = 'Easy'
        elif readability_score >= 40:
            level = 'Moderate'
        elif readability_score >= 20:
            level = 'Difficult'
        else:
            level = 'Very Difficult'
        
        return {
            'score': readability_score,
            'level': level,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complex_word_ratio': complex_word_ratio,
            'total_sentences': len(sentences),
            'total_words': len(words)
        }


class LanguageDetector:
    """Detect language of text content."""
    
    def detect(self, text: str) -> Dict[str, Any]:
        """Detect language of text."""
        # Simple language detection based on common words
        # In a full implementation, this would use a proper language detection library
        
        # Common words in different languages
        language_indicators = {
            'en': ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'],
            'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf'],
            'it': ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un', 'con', 'da', 'a', 'è']
        }
        
        words = text.lower().split()
        word_count = len(words)
        
        if word_count < 10:
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'reason': 'Insufficient text for language detection'
            }
        
        # Count matches for each language
        language_scores = {}
        for lang, indicators in language_indicators.items():
            matches = sum(1 for word in words if word in indicators)
            language_scores[lang] = matches / word_count
        
        # Find the language with highest score
        best_language = max(language_scores.items(), key=lambda x: x[1])
        
        return {
            'language': best_language[0],
            'confidence': best_language[1],
            'scores': language_scores
        }


def analyze_content_directly(content: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content directly without scraping from URL."""
    try:
        # Handle case where content might be a list instead of string
        if isinstance(content, list):
            # Join list elements into a single string
            content = ' '.join(str(item) for item in content if item)
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)
        
        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "Insufficient content to analyze (minimum 50 characters)",
                "error_type": "content_error"
            }
        
        # Create analyzer
        analyzer = ContentAnalyzer()
        
        # Analyze content directly
        result = analyzer.analyze_content_directly(content, options)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing content: {e}",
            "error_type": "analysis_error"
        }


@tool(
    name="web_analyze",
    description="Analyze web content or text for insights and patterns"
)
def web_analyze(
    url: str = None,
    content: str = None,
    analysis_types: List[str] = None,
    extract_sentiment: bool = True,
    extract_topics: bool = True,
    extract_keywords: bool = True,
    extract_entities: bool = True,
    analyze_readability: bool = False,
    detect_language: bool = False,
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Analyze web content or provided text for insights and patterns.
    
    Args:
        url: URL to analyze (optional if content is provided)
        content: Direct text content to analyze (optional if url is provided)
        analysis_types: List of analysis types to perform
        extract_sentiment: Analyze content sentiment
        extract_topics: Extract main topics and themes
        extract_keywords: Extract important keywords
        extract_entities: Extract named entities
        analyze_readability: Analyze content readability
        detect_language: Detect content language
    
    Returns:
        dict: Analysis results with insights and patterns
    """
    try:
        # Handle case where neither URL nor content is provided
        if not url and not content:
            return {
                "success": True,
                "data": {
                    "warning": "No URL or content provided for analysis",
                    "suggestion": "Use web_search() first to find URLs, then call web_analyze() with the URL or content",
                    "analysis": {
                        "sentiment": "neutral",
                        "topics": [],
                        "keywords": [],
                        "entities": [],
                        "readability_score": 0,
                        "language": "unknown"
                    }
                },
                "analyzed_at": time.time()
            }
        
        # Handle case where both URL and content are provided
        if url and content:
            return {
                "success": True,
                "data": {
                    "warning": "Both URL and content provided, analyzing content directly",
                    "analysis": analyze_content_directly(content, {
                        'extract_sentiment': extract_sentiment,
                        'extract_topics': extract_topics,
                        'extract_keywords': extract_keywords,
                        'extract_entities': extract_entities,
                        'analyze_readability': analyze_readability,
                        'detect_language': detect_language
                    }).get('data', {})
                },
                "analyzed_at": time.time()
            }
        
        # If content is provided, analyze it directly
        if content:
            return analyze_content_directly(content, {
                'extract_sentiment': extract_sentiment,
                'extract_topics': extract_topics,
                'extract_keywords': extract_keywords,
                'extract_entities': extract_entities,
                'analyze_readability': analyze_readability,
                'detect_language': detect_language
            })
        
        # Handle empty or invalid URL
        if not url or not url.strip():
            return {
                "success": True,
                "data": {
                    "warning": "Empty or invalid URL provided",
                    "suggestion": "Provide a valid URL or use web_search() first to find URLs",
                    "analysis": {
                        "sentiment": "neutral",
                        "topics": [],
                        "keywords": [],
                        "entities": [],
                        "readability_score": 0,
                        "language": "unknown"
                    }
                },
                "analyzed_at": time.time()
            }
        
        # Create analyzer
        analyzer = ContentAnalyzer()
        
        # Analyze content
        result = analyzer.analyze(url, {
            'extract_sentiment': extract_sentiment,
            'extract_topics': extract_topics,
            'extract_keywords': extract_keywords,
            'extract_entities': extract_entities,
            'analyze_readability': analyze_readability,
            'detect_language': detect_language,
            'timeout': timeout
        })
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "unexpected_error"
        }
