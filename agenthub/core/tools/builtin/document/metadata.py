"""
Document Metadata Extraction Implementation

Provides comprehensive metadata extraction from various document formats
including author, title, creation date, keywords, and content analysis.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib

from agenthub.core.tools import tool
from agenthub.core.tools.builtin.base import SecurityValidator
from .parser import document_parse


class MetadataExtractor:
    """Comprehensive metadata extraction from documents."""
    
    def __init__(self):
        self.security_validator = SecurityValidator()
    
    def extract(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from document."""
        try:
            # Validate file path
            self.security_validator._validate_file_path(file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "error_type": "file_not_found"
                }
            
            # Parse document first to get content
            parse_result = document_parse(file_path, extract_metadata=True)
            
            if not parse_result.get('success'):
                return {
                    "success": False,
                    "error": f"Failed to parse document: {parse_result.get('error')}",
                    "error_type": "parsing_error"
                }
            
            # Extract basic file metadata
            file_metadata = self._extract_file_metadata(file_path)
            
            # Extract content metadata
            content_metadata = self._extract_content_metadata(parse_result.get('content', {}))
            
            # Extract document-specific metadata
            doc_metadata = parse_result.get('metadata', {})
            
            # Combine all metadata
            metadata = {
                **file_metadata,
                **content_metadata,
                **doc_metadata
            }
            
            # Add analysis if requested
            if options.get('include_analysis', True):
                analysis = self._analyze_content(parse_result.get('content', {}))
                metadata['analysis'] = analysis
            
            return {
                "success": True,
                "metadata": metadata,
                "file_path": file_path,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Metadata extraction failed: {str(e)}",
                "error_type": "extraction_error"
            }
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata."""
        stat = os.stat(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        
        return {
            "file_name": os.path.basename(file_path),
            "file_extension": file_ext,
            "file_size": stat.st_size,
            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "file_hash": file_hash,
            "is_readable": os.access(file_path, os.R_OK),
            "is_writable": os.access(file_path, os.W_OK)
        }
    
    def _extract_content_metadata(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from document content."""
        text = content.get('text', '')
        
        if not text:
            return {}
        
        # Basic text statistics
        word_count = len(text.split())
        char_count = len(text)
        line_count = len(text.splitlines())
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Language detection (simple heuristic)
        language = self._detect_language(text)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Extract entities (simple pattern matching)
        entities = self._extract_entities(text)
        
        # Extract topics (simple keyword-based)
        topics = self._extract_topics(text)
        
        return {
            "content_stats": {
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "paragraph_count": paragraph_count,
                "average_words_per_line": round(word_count / line_count, 2) if line_count > 0 else 0,
                "average_words_per_paragraph": round(word_count / paragraph_count, 2) if paragraph_count > 0 else 0
            },
            "language": language,
            "keywords": keywords,
            "entities": entities,
            "topics": topics
        }
    
    def _analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for additional insights."""
        text = content.get('text', '')
        
        if not text:
            return {}
        
        # Sentiment analysis (simple heuristic)
        sentiment = self._analyze_sentiment(text)
        
        # Readability analysis
        readability = self._analyze_readability(text)
        
        # Content type analysis
        content_type = self._analyze_content_type(text)
        
        # Structure analysis
        structure = self._analyze_structure(content)
        
        return {
            "sentiment": sentiment,
            "readability": readability,
            "content_type": content_type,
            "structure": structure
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words."""
        # Common words in different languages
        language_indicators = {
            'english': ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'],
            'spanish': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf']
        }
        
        text_lower = text.lower()
        word_counts = {}
        
        for lang, words in language_indicators.items():
            count = sum(1 for word in words if word in text_lower)
            word_counts[lang] = count
        
        if not word_counts:
            return 'unknown'
        
        return max(word_counts, key=word_counts.get)
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text using simple frequency analysis."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract basic entities from text using pattern matching."""
        entities = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'urls': re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            'phone_numbers': re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
            'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            'money': re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', text)
        }
        
        # Clean up and deduplicate
        for entity_type, entity_list in entities.items():
            entities[entity_type] = list(set(entity_list))
        
        return entities
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text using keyword analysis."""
        # Simple topic extraction based on common topic keywords
        topic_keywords = {
            'technology': ['computer', 'software', 'hardware', 'internet', 'digital', 'data', 'system', 'programming'],
            'business': ['company', 'business', 'market', 'sales', 'profit', 'customer', 'management', 'strategy'],
            'science': ['research', 'study', 'experiment', 'analysis', 'theory', 'hypothesis', 'scientific'],
            'health': ['health', 'medical', 'doctor', 'patient', 'treatment', 'disease', 'medicine', 'hospital'],
            'education': ['school', 'university', 'student', 'teacher', 'learning', 'education', 'course', 'study'],
            'politics': ['government', 'political', 'election', 'policy', 'law', 'democracy', 'vote', 'senate']
        }
        
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topics sorted by score
        return sorted(topic_scores.keys(), key=lambda x: topic_scores[x], reverse=True)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using keyword counting."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'positive', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'negative', 'sad', 'angry', 'frustrated', 'disgusting']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        positive_ratio = positive_count / total_words if total_words > 0 else 0
        negative_ratio = negative_count / total_words if total_words > 0 else 0
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_ratio': round(positive_ratio, 3),
            'negative_ratio': round(negative_ratio, 3),
            'confidence': round(abs(positive_ratio - negative_ratio), 3)
        }
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Simple readability analysis."""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        if not sentences or not words:
            return {'readability_score': 0, 'difficulty': 'unknown'}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability score (higher = more difficult)
        readability_score = (avg_sentence_length * 0.39) + (avg_word_length * 11.8) - 15.59
        
        if readability_score < 30:
            difficulty = 'very_easy'
        elif readability_score < 50:
            difficulty = 'easy'
        elif readability_score < 70:
            difficulty = 'medium'
        elif readability_score < 90:
            difficulty = 'hard'
        else:
            difficulty = 'very_hard'
        
        return {
            'readability_score': round(readability_score, 2),
            'difficulty': difficulty,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2)
        }
    
    def _analyze_content_type(self, text: str) -> str:
        """Analyze the type of content."""
        # Check for common patterns
        if re.search(r'^\s*#+\s+', text, re.MULTILINE):
            return 'markdown'
        elif re.search(r'<[^>]+>', text):
            return 'html'
        elif re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=', text, re.MULTILINE):
            return 'code'
        elif re.search(r'^\s*\d+\.\s+', text, re.MULTILINE):
            return 'numbered_list'
        elif re.search(r'^\s*[-*]\s+', text, re.MULTILINE):
            return 'bulleted_list'
        else:
            return 'plain_text'
    
    def _analyze_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document structure."""
        structure = {}
        
        # Check for tables
        if 'tables' in content:
            structure['has_tables'] = True
            structure['table_count'] = len(content['tables'])
        else:
            structure['has_tables'] = False
            structure['table_count'] = 0
        
        # Check for links
        if 'links' in content:
            structure['has_links'] = True
            structure['link_count'] = len(content['links'])
        else:
            structure['has_links'] = False
            structure['link_count'] = 0
        
        # Check for images
        if 'images' in content:
            structure['has_images'] = True
            structure['image_count'] = len(content['images'])
        else:
            structure['has_images'] = False
            structure['image_count'] = 0
        
        return structure


# Global metadata extractor instance
_metadata_extractor = MetadataExtractor()


@tool(
    name="document_extract_metadata",
    description="Extract comprehensive metadata from documents including content analysis"
)
def document_extract_metadata(
    file_path: str,
    include_analysis: bool = True,
    include_keywords: bool = True,
    include_entities: bool = True,
    include_topics: bool = True
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from documents.
    
    Args:
        file_path: Path to the document file
        include_analysis: Whether to include content analysis
        include_keywords: Whether to extract keywords
        include_entities: Whether to extract entities
        include_topics: Whether to extract topics
    
    Returns:
        dict: Comprehensive metadata including file info, content stats, and analysis
    """
    options = {
        'include_analysis': include_analysis,
        'include_keywords': include_keywords,
        'include_entities': include_entities,
        'include_topics': include_topics
    }
    
    return _metadata_extractor.extract(file_path, options)
