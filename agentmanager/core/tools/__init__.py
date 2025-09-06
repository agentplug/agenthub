#!/usr/bin/env python3
"""
Core Tools Module - Phase 2.5
Provides tool registry, decorator, and FastMCP integration for tool injection.
"""

# Mock FastMCP implementation for development
class MockFastMCP:
    """Mock FastMCP implementation for development and testing."""
    
    def __init__(self, name: str):
        self.name = name
        self._tools = []
    
    def tool(self):
        """Mock tool decorator."""
        def decorator(func):
            self._tools.append(func)
            return func
        return decorator

# Use mock implementation for now
FastMCP = MockFastMCP
from typing import Dict, List, Callable, Any, Optional
import threading
import requests
import json
from urllib.parse import quote
from dataclasses import dataclass
from enum import Enum

# Tool metadata structure
@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    function: Callable
    namespace: str = "custom"
    parameters: Dict[str, Any] = None
    return_type: str = "dict"
    examples: List[str] = None

class ToolNamespace(Enum):
    """Tool namespace enumeration."""
    BUILTIN = "builtin"
    CUSTOM = "custom"

class ToolRegistry:
    """Singleton tool registry managing FastMCP server and tool registration."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.mcp_server = FastMCP("AgentHub Tools")
            self.registered_tools: Dict[str, ToolMetadata] = {}
            self._initialized = True
    
    def register_tool(self, name: str, func: Callable, description: str = "", namespace: str = "custom") -> Callable:
        """
        Register a tool with the FastMCP server.
        
        Args:
            name: Tool name
            func: Tool function
            description: Tool description
            namespace: Tool namespace (builtin or custom)
            
        Returns:
            The original function (for decorator usage)
        """
        # Validate tool name
        if not name or not isinstance(name, str):
            raise ValueError("Tool name must be a non-empty string")
        
        # Check for name conflicts
        if name in self.registered_tools:
            raise ValueError(f"Tool '{name}' is already registered")
        
        # Validate function
        if not callable(func):
            raise ValueError("Tool must be callable")
        
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            function=func,
            namespace=namespace,
            parameters=self._extract_parameters(func),
            return_type=self._extract_return_type(func),
            examples=self._generate_examples(name, func)
        )
        
        # Register with FastMCP
        @self.mcp_server.tool()
        def tool_wrapper(**kwargs):
            return func(**kwargs)
        
        tool_wrapper.__name__ = name
        tool_wrapper.__doc__ = description
        
        # Store metadata
        self.registered_tools[name] = metadata
        
        return func
    
    def _extract_parameters(self, func: Callable) -> Dict[str, Any]:
        """Extract parameter information from function signature."""
        import inspect
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            parameters[param_name] = {
                "type": param.annotation if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty,
                "default": param.default if param.default != inspect.Parameter.empty else None
            }
        
        return parameters
    
    def _extract_return_type(self, func: Callable) -> str:
        """Extract return type from function signature."""
        import inspect
        sig = inspect.signature(func)
        return_type = sig.return_annotation
        
        if return_type == inspect.Parameter.empty:
            return "Any"
        
        return str(return_type)
    
    def _generate_examples(self, name: str, func: Callable) -> List[str]:
        """Generate usage examples for the tool."""
        import inspect
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        if not param_names:
            return [f"{name}()"]
        
        # Generate simple examples
        examples = []
        if len(param_names) == 1:
            examples.append(f'{name}("{param_names[0]}")')
        elif len(param_names) == 2:
            examples.append(f'{name}("{param_names[0]}", "{param_names[1]}")')
        else:
            # For more complex functions, create a basic example
            args = ', '.join([f'"{param}"' for param in param_names[:3]])
            if len(param_names) > 3:
                args += ", ..."
            examples.append(f"{name}({args})")
        
        return examples
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.registered_tools.keys())
    
    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self.registered_tools.get(name)
    
    def get_mcp_server(self):
        """Get the FastMCP server instance."""
        return self.mcp_server

# Global registry instance
_registry = ToolRegistry()

def tool(name: str, description: str = ""):
    """
    Decorator for registering tools.
    
    Args:
        name: Tool name
        description: Tool description
        
    Returns:
        Decorator function
    """
    def decorator(func):
        return _registry.register_tool(name, func, description, "custom")
    return decorator

def get_available_tools() -> List[str]:
    """Get list of available tool names."""
    return _registry.get_available_tools()

def get_tool_metadata(name: str) -> Optional[ToolMetadata]:
    """Get metadata for a specific tool."""
    return _registry.get_tool_metadata(name)

def get_mcp_server():
    """Get the FastMCP server instance."""
    return _registry.get_mcp_server()

# Built-in tools
@tool(name="web_search", description="Search the web for real-time information")
def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information using DuckDuckGo API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Dictionary with search results including titles, snippets, and URLs
    """
    try:
        # Use DuckDuckGo Instant Answer API (free, no API key required)
        url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        results = {
            "query": query,
            "abstract": data.get("Abstract", ""),
            "abstract_text": data.get("AbstractText", ""),
            "abstract_source": data.get("AbstractSource", ""),
            "abstract_url": data.get("AbstractURL", ""),
            "related_topics": data.get("RelatedTopics", [])[:max_results],
            "results": []
        }
        
        # Add related topics as results
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "Text" in topic:
                results["results"].append({
                    "title": topic.get("Text", ""),
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })
        
        # If no related topics, create a basic result
        if not results["results"] and results["abstract"]:
            results["results"].append({
                "title": f"Search results for: {query}",
                "snippet": results["abstract"],
                "url": results["abstract_url"]
            })
        
        return results
        
    except Exception as e:
        return {
            "error": f"Web search failed: {str(e)}",
            "query": query,
            "results": []
        }

@tool(name="data_analyzer", description="Analyze data and provide insights")
def data_analyzer(data: str) -> dict:
    """
    Analyze data and provide basic insights.
    
    Args:
        data: Data string to analyze
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Basic analysis
        word_count = len(data.split())
        char_count = len(data)
        line_count = len(data.split('\n'))
        
        # Simple sentiment analysis (basic keyword matching)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'poor', 'worst', 'horrible']
        
        words = data.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        sentiment = "neutral"
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        
        return {
            "insights": f"Analyzed: {data[:100]}{'...' if len(data) > 100 else ''}",
            "word_count": word_count,
            "char_count": char_count,
            "line_count": line_count,
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Data analysis failed: {str(e)}",
            "status": "error"
        }

# Export main functions
__all__ = [
    "tool",
    "get_available_tools", 
    "get_tool_metadata",
    "get_mcp_server",
    "ToolRegistry",
    "ToolMetadata",
    "ToolNamespace",
    "web_search",
    "data_analyzer"
]
