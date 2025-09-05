"""MCP Client implementation for AgentHub using official MCP SDK.

This module provides MCP client functionality using the official
Model Context Protocol Python SDK.
"""

import asyncio
import logging
import subprocess
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client implementation using the official MCP SDK."""
    
    def __init__(self, timeout: float = 30.0):
        """Initialize MCP client."""
        self.timeout = timeout
        self.connected = False
        self.session: Optional[ClientSession] = None
        self.server_process: Optional[subprocess.Popen] = None
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging for the client."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def connect(self, server_command: List[str]) -> None:
        """Connect to an MCP server."""
        if self.connected:
            logger.warning("Client is already connected")
            return
        
        try:
            logger.info(f"Connecting to MCP server: {' '.join(server_command)}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_command[0],
                args=server_command[1:] if len(server_command) > 1 else []
            )
            
            # Connect using stdio client
            self._stdio_client_context = stdio_client(server_params)
            self.read, self.write = await self._stdio_client_context.__aenter__()
            self.session = ClientSession(self.read, self.write)
            
            # Initialize the session
            await self.session.initialize()
            
            self.connected = True
            logger.info("Successfully connected to MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            await self.disconnect()
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self.connected:
            return
        
        logger.info("Disconnecting from MCP server")
        
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
            finally:
                self.session = None
        
        # Clean up stdio client context
        if hasattr(self, '_stdio_client_context') and self._stdio_client_context:
            try:
                await self._stdio_client_context.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing stdio context: {e}")
            finally:
                self._stdio_client_context = None
        
        self.connected = False
        logger.info("Disconnected from MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            tools_response = await self.session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools_response.tools
            ]
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Extract text content from the result
            if hasattr(result, 'content') and result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        return content.text
            
            # If no text content, return the raw result
            return str(result)
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            raise
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            resources_response = await self.session.list_resources()
            return [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": getattr(resource, 'description', None),
                    "mimeType": getattr(resource, 'mimeType', None)
                }
                for resource in resources_response.resources
            ]
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            raise
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            result = await self.session.read_resource(uri)
            return {
                "uri": uri,
                "contents": [
                    {
                        "uri": content.uri,
                        "mimeType": content.mimeType,
                        "text": content.text if hasattr(content, 'text') else None
                    }
                    for content in result.contents
                ]
            }
        except Exception as e:
            logger.error(f"Failed to read resource: {e}")
            raise
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts from the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            prompts_response = await self.session.list_prompts()
            return [
                {
                    "name": prompt.name,
                    "description": prompt.description,
                    "arguments": getattr(prompt, 'arguments', None)
                }
                for prompt in prompts_response.prompts
            ]
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            raise
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a prompt from the server."""
        if not self.connected or not self.session:
            raise Exception("Not connected to server")
        
        try:
            result = await self.session.get_prompt(name, arguments or {})
            return {
                "description": result.description,
                "messages": [
                    {
                        "role": message.role,
                        "content": {
                            "type": "text",
                            "text": message.content.text if hasattr(message.content, 'text') else str(message.content)
                        }
                    }
                    for message in result.messages
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get prompt: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if client is connected to server."""
        return self.connected and self.session is not None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


class MCPClientManager:
    """Manager for multiple MCP client connections."""
    
    def __init__(self):
        """Initialize the client manager."""
        self.clients: Dict[str, MCPClient] = {}
    
    async def create_client(self, name: str, server_command: List[str]) -> MCPClient:
        """Create and connect a new MCP client."""
        if name in self.clients:
            raise ValueError(f"Client '{name}' already exists")
        
        client = MCPClient()
        await client.connect(server_command)
        
        self.clients[name] = client
        return client
    
    async def get_client(self, name: str) -> Optional[MCPClient]:
        """Get a client by name."""
        return self.clients.get(name)
    
    async def disconnect_client(self, name: str) -> bool:
        """Disconnect and remove a client."""
        client = self.clients.get(name)
        if client:
            await client.disconnect()
            del self.clients[name]
            return True
        return False
    
    async def disconnect_all(self) -> None:
        """Disconnect all clients."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()
    
    def list_clients(self) -> List[str]:
        """List all client names."""
        return list(self.clients.keys())
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_all()
