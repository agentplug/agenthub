"""
Built-in Tools for AgentHub

This module provides powerful built-in tools that work without MCP server.
All tools use the existing @tool decorator system for seamless integration.
"""

# Import web tools
from .web import *

# Import document tools
from .document import *

# Import other tool categories (to be implemented)
# from .code import *
# from .data import *
# from .external import *

__all__ = [
    # Web tools
    'web_search',
    'web_search_async',
    'web_scrape',
    'web_scrape_async',
    'web_summarize',
    'web_analyze',
    
    # Document tools
    'document_parse',
    'document_search',
    'document_chunk',
    'document_extract_metadata',
    
    # Base classes
    'BaseTool',
    'CachedTool',
    'SecureTool',
    'ToolCache',
    'SecurityValidator',
    'ValidationError',
    'SecurityError'
]
