"""
Base Classes for Built-in Tools

Provides base classes and utilities for all built-in tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time
import hashlib
from threading import Lock


class BaseTool(ABC):
    """Base class for all built-in tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.cache = None
        self.security_validator = None
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True
    
    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key for the operation."""
        return f"{self.name}:{hash(str(sorted(kwargs.items())))}"


class CachedTool(BaseTool):
    """Base class for tools with caching support."""
    
    def __init__(self, name: str, description: str, cache_ttl: int = 300):
        super().__init__(name, description)
        self.cache_ttl = cache_ttl
        self.cache = ToolCache()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with caching support."""
        cache_key = self.get_cache_key(**kwargs)
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Execute tool
        result = self._execute_impl(**kwargs)
        
        # Cache result
        self.cache.set(cache_key, result, self.cache_ttl)
        
        return result
    
    @abstractmethod
    def _execute_impl(self, **kwargs) -> Dict[str, Any]:
        """Implementation of tool execution."""
        pass


class SecureTool(BaseTool):
    """Base class for tools with security validation."""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.security_validator = SecurityValidator()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with security validation."""
        # Validate inputs
        if not self.validate_input(**kwargs):
            raise ValidationError("Input validation failed")
        
        # Security check
        if not self.security_validator.validate(self.name, **kwargs):
            raise SecurityError("Security validation failed")
        
        return self._execute_impl(**kwargs)
    
    @abstractmethod
    def _execute_impl(self, **kwargs) -> Dict[str, Any]:
        """Implementation of tool execution."""
        pass


class ToolCache:
    """Intelligent caching system for tool operations."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = Lock()
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if time.time() > entry.expires_at:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return None
            
            self.access_times[key] = time.time()
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value."""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            self.cache[key] = CacheEntry(value, expires_at)
            self.access_times[key] = time.time()
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        if lru_key in self.cache:
            del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()


class CacheEntry:
    """Cache entry with expiration."""
    
    def __init__(self, value: Any, expires_at: float):
        self.value = value
        self.expires_at = expires_at


class SecurityValidator:
    """Security validation for tool operations."""
    
    def __init__(self):
        self.blocked_patterns = [
            r'\.\./',  # Path traversal
            r'file://',  # File protocol
            r'javascript:',  # JavaScript protocol
            r'data:',  # Data protocol
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'os\.system\(',
            r'subprocess\.'
        ]
        self.allowed_domains = set()
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def validate(self, tool_name: str, **kwargs) -> bool:
        """Validate tool execution parameters."""
        try:
            # Validate based on tool type
            if 'url' in kwargs:
                self._validate_url(kwargs['url'])
            
            if 'file_path' in kwargs:
                self._validate_file_path(kwargs['file_path'])
            
            if 'code' in kwargs:
                self._validate_code(kwargs['code'])
            
            if 'query' in kwargs:
                self._validate_query(kwargs['query'])
            
            return True
        
        except SecurityError:
            return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL for security."""
        from urllib.parse import urlparse
        import re
        
        parsed = urlparse(url)
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Check domain whitelist
        if self.allowed_domains and parsed.netloc not in self.allowed_domains:
            return False
        
        return True
    
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
    
    def _validate_url(self, url: str) -> None:
        """Validate URL for security."""
        if not self.validate_url(url):
            raise SecurityError("Invalid or unsafe URL")
    
    def _validate_file_path(self, file_path: str) -> None:
        """Validate file path for security."""
        import os
        
        # Check for path traversal
        if '..' in file_path or file_path.startswith('/'):
            raise SecurityError("Path traversal not allowed")
        
        # Check file size
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                raise SecurityError("File too large")
    
    def _validate_code(self, code: str) -> None:
        """Validate code for security."""
        import re
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'__import__',
            r'eval\(',
            r'exec\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Dangerous code pattern: {pattern}")


class ValidationError(Exception):
    """Input validation error."""
    pass


class SecurityError(Exception):
    """Security validation error."""
    pass
