"""Tool Registry - Singleton for managing tools and FastMCP server."""

import threading
from typing import Dict, List, Callable, Any, Optional
from mcp.server import FastMCP
from .exceptions import ToolNameConflictError, ToolValidationError, ToolNotFoundError
from .metadata import ToolMetadata
from multiprocessing import Process


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
            # Tool access control: agent_id -> list of allowed tool names
            self.agent_tool_access: Dict[str, List[str]] = {}
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
    
    def assign_tools_to_agent(self, agent_id: str, tool_names: List[str]) -> None:
        """Assign specific tools to an agent."""
        # Validate that all tools exist
        for tool_name in tool_names:
            if tool_name not in self.registered_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found")
        
        # Assign tools to agent
        self.agent_tool_access[agent_id] = tool_names.copy()
        print(f"🔐 Assigned tools to agent '{agent_id}': {tool_names}")
    
    def get_agent_tools(self, agent_id: str) -> List[str]:
        """Get tools assigned to a specific agent."""
        return self.agent_tool_access.get(agent_id, [])
    
    def can_agent_access_tool(self, agent_id: str, tool_name: str) -> bool:
        """Check if an agent can access a specific tool."""
        agent_tools = self.agent_tool_access.get(agent_id, [])
        return tool_name in agent_tools
    
    def get_agent_tool_metadata(self, agent_id: str) -> List[ToolMetadata]:
        """Get tool metadata for tools assigned to an agent."""
        agent_tools = self.agent_tool_access.get(agent_id, [])
        return [self.tool_metadata[tool_name] for tool_name in agent_tools if tool_name in self.tool_metadata]


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

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _registry


def assign_tools_to_agent(agent_id: str, tool_names: List[str]) -> None:
    """Assign specific tools to an agent."""
    _registry.assign_tools_to_agent(agent_id, tool_names)


def get_agent_tools(agent_id: str) -> List[str]:
    """Get tools assigned to a specific agent."""
    return _registry.get_agent_tools(agent_id)


def can_agent_access_tool(agent_id: str, tool_name: str) -> bool:
    """Check if an agent can access a specific tool."""
    return _registry.can_agent_access_tool(agent_id, tool_name)


def get_agent_tool_metadata(agent_id: str) -> List[ToolMetadata]:
    """Get tool metadata for tools assigned to an agent."""
    return _registry.get_agent_tool_metadata(agent_id)

def run_resources():
    """Run the MCP server"""
    mcp_server = get_mcp_server()
    mcp_server.run(transport="sse")