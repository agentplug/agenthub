"""Tool registry for managing registered tools."""

import logging
from typing import Dict, Any, List, Optional, Callable
from .decorators import ToolMetadata

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all registered tools."""
    
    def __init__(self) -> None:
        self._tools: Dict[str, ToolMetadata] = {}
        self._tool_functions: Dict[str, Callable[..., Any]] = {}

    def register(self, metadata: ToolMetadata) -> None:
        """Register a tool with its metadata."""
        if metadata.name in self._tools:
            raise ValueError(f"Tool '{metadata.name}' is already registered")

        self._tools[metadata.name] = metadata
        self._tool_functions[metadata.name] = metadata.function
        logger.info(f"Registered tool: {metadata.name}")

    def get_tool(self, name: str) -> Optional[ToolMetadata]:
        """Get tool metadata by name."""
        return self._tools.get(name)

    def get_function(self, name: str) -> Optional[Callable[..., Any]]:
        """Get tool function by name."""
        return self._tool_functions.get(name)

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())

    def get_all_metadata(self) -> Dict[str, ToolMetadata]:
        """Get all tool metadata."""
        return self._tools.copy()

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._tool_functions.clear()
        logger.info("Cleared all tools from registry")
    
    def get_tool_count(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)
    
    def get_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given parameters."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        
        metadata = self._tools[name]
        logger.info(f"Executing tool: {name}")
        try:
            result = metadata.function(**kwargs)
            logger.info(f"Tool {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}")
            raise
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get MCP-compatible schemas for all tools."""
        schemas = {}
        for name, metadata in self._tools.items():
            if metadata.input_schema:
                schemas[name] = metadata.input_schema
            else:
                # Generate basic schema from parameters
                schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                for param_name, param_info in metadata.parameters.items():
                    if param_info.get("default") is None:
                        schema["required"].append(param_name)
                    schema["properties"][param_name] = {
                        "type": "string",  # Default to string, could be improved
                        "description": f"Parameter {param_name}"
                    }
                schemas[name] = schema
        return schemas


# Global tool registry instance
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _global_registry
