"""Tool Registry - Singleton for managing tools and FastMCP server."""

import threading
from typing import Dict, List, Callable, Any, Optional
from mcp.server import FastMCP
from .exceptions import ToolNameConflictError, ToolValidationError, ToolNotFoundError
from .metadata import ToolMetadata


class ToolRegistry:
    """Singleton registry for managing tools and FastMCP server."""
    
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
            self.registered_tools: Dict[str, Callable] = {}
            self.tool_metadata: Dict[str, ToolMetadata] = {}
            self._initialized = True
    
    def register_tool(self, name: str, func: Callable, description: str = "", namespace: str = "custom") -> Callable:
        """Register a tool with the registry and FastMCP server."""
        # Validate tool name
        if not name or not isinstance(name, str):
            raise ToolValidationError("Tool name must be a non-empty string")
        
        if name in self.registered_tools:
            raise ToolNameConflictError(f"Tool '{name}' is already registered")
        
        # Validate tool function
        if not callable(func):
            raise ToolValidationError("Tool must be callable")
        
        # Check if function has parameters (not just empty function)
        import inspect
        sig = inspect.signature(func)
        if len(sig.parameters) == 0:
            raise ToolValidationError("Tool function must have at least one parameter")
        
        # Register with internal registry
        self.registered_tools[name] = func
        
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            function=func,
            namespace=namespace
        )
        self.tool_metadata[name] = metadata
        
        # Register with FastMCP server
        # Register the original function directly with FastMCP
        self.mcp_server.tool(name=name, description=description)(func)
        
        # Tool is now registered with FastMCP
        
        return func
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.registered_tools.keys())
    
    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self.tool_metadata.get(name)
    
    def get_tool_function(self, name: str) -> Optional[Callable]:
        """Get the function for a specific tool."""
        return self.registered_tools.get(name)
    
    def is_tool_registered(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self.registered_tools
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool (for testing purposes)."""
        if name in self.registered_tools:
            del self.registered_tools[name]
            del self.tool_metadata[name]
            return True
        return False


# Global registry instance
_registry = ToolRegistry()


def get_available_tools() -> List[str]:
    """Get list of available tool names."""
    return _registry.get_available_tools()


def get_mcp_server():
    """Get the FastMCP server instance."""
    return _registry.mcp_server


def get_tool_metadata(name: str) -> Optional[ToolMetadata]:
    """Get metadata for a specific tool."""
    return _registry.get_tool_metadata(name)


def get_tool_function(name: str) -> Optional[Callable]:
    """Get the function for a specific tool."""
    return _registry.get_tool_function(name)
