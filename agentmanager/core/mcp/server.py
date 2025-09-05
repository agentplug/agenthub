"""MCP Server implementation for AgentHub using official MCP SDK.

This module provides MCP server functionality using the official
Model Context Protocol Python SDK.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server implementation using the official MCP SDK."""
    
    def __init__(self, name: str = "AgentHub MCP Server", version: str = "1.0.0"):
        """Initialize MCP server."""
        self.name = name
        self.version = version
        self.mcp = FastMCP(name)
        self.tools: Dict[str, Callable] = {}
        self.running = False
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging for the server."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def register_tool(self, name: str, description: str, function: Callable) -> None:
        """Register a tool with the server using the official MCP SDK."""
        # Use the FastMCP decorator to register the tool
        self.mcp.tool(name=name, description=description)(function)
        self.tools[name] = function
        logger.info(f"Registered tool: {name}")
    
    def register_resource(self, uri: str, name: str, description: str, 
                         function: Callable) -> None:
        """Register a resource with the server."""
        # Use the FastMCP resource decorator
        self.mcp.resource(uri, name=name, description=description)(function)
        logger.info(f"Registered resource: {uri}")
    
    def register_prompt(self, name: str, description: str, function: Callable) -> None:
        """Register a prompt with the server."""
        # Use the FastMCP prompt decorator
        self.mcp.prompt(name=name, description=description)(function)
        logger.info(f"Registered prompt: {name}")
    
    async def start(self) -> None:
        """Start the MCP server."""
        if self.running:
            logger.warning("Server is already running")
            return
        
        self.running = True
        logger.info(f"Starting {self.name} v{self.version}")
        logger.info(f"Registered {len(self.tools)} tools")
        
        try:
            # Run the FastMCP server
            await self.mcp.run()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            self.running = False
            logger.info("Server stopped")
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if not self.running:
            logger.warning("Server is not running")
            return
        
        logger.info("Stopping server...")
        self.running = False
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running
    
    def get_tool_count(self) -> int:
        """Get the number of registered tools."""
        return len(self.tools)
    
    def get_mcp_instance(self) -> FastMCP:
        """Get the underlying FastMCP instance."""
        return self.mcp


class MCPToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, description: str, function: Callable, 
                     input_schema: Optional[Dict[str, Any]] = None) -> None:
        """Register a tool in the registry."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "function": function,
            "input_schema": input_schema or {}
        }
        logger.info(f"Registered tool in registry: {name}")
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool from the registry."""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all registered tools."""
        return self.tools.copy()
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool from registry: {name}")
            return True
        return False
