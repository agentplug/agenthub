"""Tool discovery system for finding @tool decorated functions."""

import inspect
import logging
from typing import Dict, Any, List, Optional, Union, Type, Callable
from .decorators import ToolMetadata, get_tool_metadata, is_tool

logger = logging.getLogger(__name__)


class ToolDiscovery:
    """Tool discovery system for finding @tool decorated functions."""
    
    def __init__(self):
        self.discovered_tools: Dict[str, ToolMetadata] = {}
        self._discovery_cache: Dict[str, List[ToolMetadata]] = {}
    
    def discover_tools(self, sources: List[Union[Callable, Type, Any]]) -> List[ToolMetadata]:
        """Discover tools from a list of sources (functions, modules, objects)."""
        discovered = []
        for source in sources:
            if callable(source) and is_tool(source):
                metadata = get_tool_metadata(source)
                if metadata:
                    discovered.append(metadata)
                    self.discovered_tools[metadata.name] = metadata
                    logger.info(f"Discovered tool: {metadata.name}")
        return discovered
    
    def discover_tools_from_module(self, module: Any) -> List[ToolMetadata]:
        """Discover tools from a module."""
        discovered = []
        for name, obj in inspect.getmembers(module):
            if callable(obj) and is_tool(obj):
                metadata = get_tool_metadata(obj)
                if metadata:
                    discovered.append(metadata)
                    self.discovered_tools[metadata.name] = metadata
                    logger.info(f"Discovered tool from module: {metadata.name}")
        return discovered
    
    def discover_tools_from_object(self, obj: Any) -> List[ToolMetadata]:
        """Discover tools from an object."""
        discovered = []
        for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
            if is_tool(method):
                metadata = get_tool_metadata(method)
                if metadata:
                    discovered.append(metadata)
                    self.discovered_tools[metadata.name] = metadata
                    logger.info(f"Discovered tool from object: {metadata.name}")
        return discovered
    
    def get_tool(self, name: str) -> Optional[ToolMetadata]:
        """Get a discovered tool by name."""
        return self.discovered_tools.get(name)
    
    def list_tools(self) -> List[ToolMetadata]:
        """List all discovered tools."""
        return list(self.discovered_tools.values())
    
    def get_tool_names(self) -> List[str]:
        """Get list of discovered tool names."""
        return list(self.discovered_tools.keys())
    
    def clear_tools(self):
        """Clear all discovered tools."""
        self.discovered_tools.clear()
        self._discovery_cache.clear()
        logger.info("Cleared all discovered tools")
