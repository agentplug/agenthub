"""
Document Search Implementation

Provides semantic document search capabilities with vector-based similarity
matching and intelligent content retrieval.
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from agenthub.core.tools import tool
from agenthub.core.tools.builtin.base import CachedTool, SecurityValidator
from .parser import document_parse


class DocumentSearchEngine:
    """Semantic document search engine with vector-based similarity matching."""
    
    def __init__(self):
        self.security_validator = SecurityValidator()
        self.cache = {}
        self.embeddings_cache = {}
        self.model = None
        
        # Initialize sentence transformer model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self.model = None
    
    def search(self, query: str, source_path: str = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search documents using semantic similarity and keyword matching."""
        if options is None:
            options = {}
        
        try:
            # Validate query
            if not self.security_validator.validate_query(query):
                return {
                    "success": False,
                    "error": "Invalid search query",
                    "error_type": "invalid_query"
                }
            
            # Set default options
            max_results = options.get('max_results', 10)
            similarity_threshold = options.get('similarity_threshold', 0.7)
            document_types = options.get('document_types', None)
            chunk_size = options.get('chunk_size', 1000)
            include_metadata = options.get('include_metadata', True)
            
            # Find documents to search
            documents = self._find_documents(source_path, document_types)
            
            if not documents:
                return {
                    "success": True,
                    "results": [],
                    "total_found": 0,
                    "query": query,
                    "message": "No documents found to search"
                }
            
            # Search documents
            results = []
            for doc_path in documents:
                doc_results = self._search_document(
                    doc_path, query, similarity_threshold, chunk_size, include_metadata
                )
                results.extend(doc_results)
            
            # Sort by similarity score
            results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            # Limit results
            results = results[:max_results]
            
            return {
                "success": True,
                "results": results,
                "total_found": len(results),
                "query": query,
                "documents_searched": len(documents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "error_type": "search_error"
            }
    
    def _find_documents(self, source_path: str, document_types: List[str] = None) -> List[str]:
        """Find documents to search in the specified path."""
        if not source_path:
            return []
        
        if not os.path.exists(source_path):
            return []
        
        documents = []
        supported_extensions = {'.txt', '.md', '.html', '.htm', '.json', '.csv', '.pdf', '.docx', '.doc'}
        
        if document_types:
            # Filter by specified types
            supported_extensions = {f'.{ext.lstrip(".")}' for ext in document_types}
        
        if os.path.isfile(source_path):
            # Single file
            if Path(source_path).suffix.lower() in supported_extensions:
                documents.append(source_path)
        else:
            # Directory
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if Path(file_path).suffix.lower() in supported_extensions:
                        documents.append(file_path)
        
        return documents
    
    def _search_document(self, doc_path: str, query: str, similarity_threshold: float, 
                        chunk_size: int, include_metadata: bool) -> List[Dict[str, Any]]:
        """Search within a single document."""
        try:
            # Parse document
            parse_result = document_parse(doc_path, extract_metadata=include_metadata)
            
            if not parse_result.get('success'):
                return []
            
            content = parse_result.get('content', {})
            text = content.get('text', '')
            
            if not text:
                return []
            
            # Chunk the text
            chunks = self._chunk_text(text, chunk_size)
            
            # Search chunks
            results = []
            for i, chunk in enumerate(chunks):
                similarity_score = self._calculate_similarity(query, chunk)
                
                if similarity_score >= similarity_threshold:
                    result = {
                        "document_path": doc_path,
                        "chunk_index": i,
                        "content": chunk,
                        "similarity_score": similarity_score,
                        "start_position": i * chunk_size,
                        "end_position": min((i + 1) * chunk_size, len(text))
                    }
                    
                    if include_metadata:
                        result["metadata"] = parse_result.get('metadata', {})
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            return []
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        overlap = chunk_size // 4  # 25% overlap
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """Calculate similarity between query and text."""
        # Simple keyword-based similarity as fallback
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words or not text_words:
            return 0.0
        
        # Jaccard similarity
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # If sentence transformers is available, use semantic similarity
        if self.model:
            try:
                query_embedding = self.model.encode([query])
                text_embedding = self.model.encode([text])
                
                # Cosine similarity
                import numpy as np
                cosine_sim = np.dot(query_embedding[0], text_embedding[0]) / (
                    np.linalg.norm(query_embedding[0]) * np.linalg.norm(text_embedding[0])
                )
                
                # Combine keyword and semantic similarity
                return (jaccard_similarity * 0.3 + cosine_sim * 0.7)
            except Exception:
                pass
        
        return jaccard_similarity


# Global search engine instance
_search_engine = DocumentSearchEngine()


@tool(
    name="document_search",
    description="Search documents using semantic similarity and keyword matching"
)
def document_search(
    query: str,
    source_path: str = None,
    document_types: List[str] = None,
    max_results: int = 10,
    similarity_threshold: float = 0.7,
    include_metadata: bool = True,
    chunk_size: int = 1000
) -> Dict[str, Any]:
    """
    Search documents using semantic similarity and keyword matching.
    
    Args:
        query: Search query string
        source_path: Directory path to search (optional)
        document_types: List of file extensions to include (e.g., ['pdf', 'docx'])
        max_results: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0.0-1.0)
        include_metadata: Whether to include document metadata
        chunk_size: Size of text chunks for search
    
    Returns:
        dict: Search results with content, metadata, and similarity scores
    """
    options = {
        'max_results': max_results,
        'similarity_threshold': similarity_threshold,
        'document_types': document_types,
        'chunk_size': chunk_size,
        'include_metadata': include_metadata
    }
    
    return _search_engine.search(query, source_path, options)
