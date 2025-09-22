"""
Document Chunker Implementation

Provides intelligent document chunking with multiple strategies for optimal
text segmentation and retrieval.
"""

import re
from typing import Dict, List, Any, Optional
from agenthub.core.tools import tool
from agenthub.core.tools.builtin.base import SecurityValidator


class DocumentChunker:
    """Intelligent document chunker with multiple segmentation strategies."""
    
    def __init__(self):
        self.security_validator = SecurityValidator()
    
    def chunk(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Chunk content using specified strategy."""
        try:
            # Validate content
            if not content or not content.strip():
                return {
                    "success": False,
                    "error": "Empty or invalid content",
                    "error_type": "invalid_content"
                }
            
            chunk_size = options.get('chunk_size', 1000)
            overlap = options.get('overlap', 200)
            strategy = options.get('strategy', 'semantic')
            preserve_structure = options.get('preserve_structure', True)
            
            # Validate parameters
            if chunk_size <= 0:
                return {
                    "success": False,
                    "error": "Chunk size must be positive",
                    "error_type": "invalid_parameters"
                }
            
            if overlap < 0 or overlap >= chunk_size:
                return {
                    "success": False,
                    "error": "Overlap must be non-negative and less than chunk size",
                    "error_type": "invalid_parameters"
                }
            
            # Choose chunking strategy
            if strategy == 'semantic':
                chunks = self._semantic_chunk(content, chunk_size, overlap, preserve_structure)
            elif strategy == 'sentence':
                chunks = self._sentence_chunk(content, chunk_size, overlap, preserve_structure)
            elif strategy == 'paragraph':
                chunks = self._paragraph_chunk(content, chunk_size, overlap, preserve_structure)
            elif strategy == 'fixed':
                chunks = self._fixed_chunk(content, chunk_size, overlap)
            else:
                return {
                    "success": False,
                    "error": f"Unknown chunking strategy: {strategy}",
                    "error_type": "invalid_strategy"
                }
            
            # Calculate statistics
            total_chunks = len(chunks)
            avg_chunk_size = sum(len(chunk) for chunk in chunks) / total_chunks if total_chunks > 0 else 0
            
            return {
                "success": True,
                "chunks": chunks,
                "statistics": {
                    "total_chunks": total_chunks,
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "strategy": strategy,
                    "average_chunk_size": round(avg_chunk_size, 2),
                    "total_content_length": len(content)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chunking failed: {str(e)}",
                "error_type": "chunking_error"
            }
    
    def _semantic_chunk(self, content: str, chunk_size: int, overlap: int, preserve_structure: bool) -> List[str]:
        """Semantic chunking that tries to preserve meaning boundaries."""
        # Split into sentences first
        sentences = self._split_sentences(content)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed chunk size, start a new chunk
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk, overlap)
                    current_chunk = overlap_text + " " + sentence
                    current_size = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_size = sentence_size
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_size += sentence_size
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _sentence_chunk(self, content: str, chunk_size: int, overlap: int, preserve_structure: bool) -> List[str]:
        """Chunk by sentences, respecting chunk size limits."""
        sentences = self._split_sentences(content)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed chunk size, start a new chunk
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                
                # Start new chunk with overlap
                if overlap > 0:
                    overlap_sentences = self._get_overlap_sentences(current_chunk, overlap)
                    current_chunk = overlap_sentences + [sentence]
                else:
                    current_chunk = [sentence]
                current_size = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _paragraph_chunk(self, content: str, chunk_size: int, overlap: int, preserve_structure: bool) -> List[str]:
        """Chunk by paragraphs, respecting chunk size limits."""
        paragraphs = content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            # If adding this paragraph would exceed chunk size, start a new chunk
            if current_size + paragraph_size > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Start new chunk with overlap
                if overlap > 0:
                    overlap_paragraphs = self._get_overlap_paragraphs(current_chunk, overlap)
                    current_chunk = overlap_paragraphs + [paragraph]
                else:
                    current_chunk = [paragraph]
                current_size = sum(len(p) for p in current_chunk)
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size
        
        # Add the last chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _fixed_chunk(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Fixed-size chunking with overlap."""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting using regex
        sentence_endings = r'[.!?]+'
        sentences = re.split(sentence_endings, text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get overlap text from the end of the current chunk."""
        if len(text) <= overlap_size:
            return text
        
        # Try to break at word boundary
        overlap_text = text[-overlap_size:]
        space_index = overlap_text.find(' ')
        
        if space_index > 0:
            return overlap_text[space_index:].strip()
        
        return overlap_text
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get overlap sentences from the end of the current chunk."""
        if not sentences:
            return []
        
        overlap_text = ""
        overlap_sentences = []
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            if len(overlap_text) + len(sentence) <= overlap_size:
                overlap_sentences.insert(0, sentence)
                overlap_text = sentence + " " + overlap_text
            else:
                break
        
        return overlap_sentences
    
    def _get_overlap_paragraphs(self, paragraphs: List[str], overlap_size: int) -> List[str]:
        """Get overlap paragraphs from the end of the current chunk."""
        if not paragraphs:
            return []
        
        overlap_text = ""
        overlap_paragraphs = []
        
        # Start from the end and work backwards
        for paragraph in reversed(paragraphs):
            if len(overlap_text) + len(paragraph) <= overlap_size:
                overlap_paragraphs.insert(0, paragraph)
                overlap_text = paragraph + "\n\n" + overlap_text
            else:
                break
        
        return overlap_paragraphs


# Global chunker instance
_chunker = DocumentChunker()


@tool(
    name="document_chunk",
    description="Split documents into searchable chunks with intelligent segmentation"
)
def document_chunk(
    content: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    strategy: str = "semantic",
    preserve_structure: bool = True
) -> Dict[str, Any]:
    """
    Split document into overlapping chunks for better retrieval.
    
    Args:
        content: Text content to chunk
        chunk_size: Target size for each chunk in characters
        overlap: Number of characters to overlap between chunks
        strategy: Chunking strategy ('semantic', 'sentence', 'paragraph', 'fixed')
        preserve_structure: Whether to preserve document structure
    
    Returns:
        dict: Chunked content with statistics and metadata
    """
    options = {
        'chunk_size': chunk_size,
        'overlap': overlap,
        'strategy': strategy,
        'preserve_structure': preserve_structure
    }
    
    return _chunker.chunk(content, options)
