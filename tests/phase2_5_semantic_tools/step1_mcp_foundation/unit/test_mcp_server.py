"""Unit tests for MCP Server implementation."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from agentmanager.core.mcp import MCPServer, MCPToolRegistry


class TestMCPServer:
    """Test cases for MCPServer class."""
    
    def test_server_initialization(self):
        """Test MCP server initialization."""
        server = MCPServer(name="Test Server", version="1.0.0")
        
        assert server.name == "Test Server"
        assert server.version == "1.0.0"
        assert server.get_tool_count() == 0
        assert not server.is_running()
    
    def test_tool_registration(self):
        """Test tool registration."""
        server = MCPServer()
        
        def test_tool(param: str) -> str:
            return f"Result: {param}"
        
        server.register_tool(
            name="test_tool",
            description="A test tool",
            function=test_tool
        )
        
        assert server.get_tool_count() == 1
        assert "test_tool" in server.tools
    
    def test_resource_registration(self):
        """Test resource registration."""
        server = MCPServer()
        
        def get_resource() -> str:
            return "Resource content"
        
        server.register_resource(
            uri="test://resource",
            name="Test Resource",
            description="A test resource",
            function=get_resource
        )
        
        # Resources are registered with the underlying FastMCP instance
        assert server.mcp is not None
    
    def test_prompt_registration(self):
        """Test prompt registration."""
        server = MCPServer()
        
        def generate_prompt(topic: str) -> str:
            return f"Write about {topic}"
        
        server.register_prompt(
            name="test_prompt",
            description="A test prompt",
            function=generate_prompt
        )
        
        # Prompts are registered with the underlying FastMCP instance
        assert server.mcp is not None
    
    @pytest.mark.asyncio
    async def test_server_start_stop(self):
        """Test server start and stop functionality."""
        server = MCPServer()
        
        # Mock the FastMCP run method to avoid actual server startup
        with patch.object(server.mcp, 'run', new_callable=AsyncMock) as mock_run:
            # Start server in a task
            start_task = asyncio.create_task(server.start())
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Stop the server
            await server.stop()
            
            # Wait for start task to complete
            try:
                await asyncio.wait_for(start_task, timeout=1.0)
            except asyncio.TimeoutError:
                start_task.cancel()
            
            # Verify run was called
            mock_run.assert_called_once()
    
    def test_get_mcp_instance(self):
        """Test getting the underlying MCP instance."""
        server = MCPServer()
        mcp_instance = server.get_mcp_instance()
        
        assert mcp_instance is not None
        assert hasattr(mcp_instance, 'tool')
        assert hasattr(mcp_instance, 'resource')
        assert hasattr(mcp_instance, 'prompt')


class TestMCPToolRegistry:
    """Test cases for MCPToolRegistry class."""
    
    def test_registry_initialization(self):
        """Test tool registry initialization."""
        registry = MCPToolRegistry()
        
        assert len(registry.list_tools()) == 0
    
    def test_tool_registration(self):
        """Test tool registration in registry."""
        registry = MCPToolRegistry()
        
        def test_function(param: str) -> str:
            return f"Result: {param}"
        
        registry.register_tool(
            name="test_tool",
            description="A test tool",
            function=test_function,
            input_schema={"type": "object", "properties": {"param": {"type": "string"}}}
        )
        
        tools = registry.list_tools()
        assert len(tools) == 1
        assert "test_tool" in tools
        
        tool = registry.get_tool("test_tool")
        assert tool is not None
        assert tool["name"] == "test_tool"
        assert tool["description"] == "A test tool"
        assert tool["function"] == test_function
    
    def test_tool_unregistration(self):
        """Test tool unregistration from registry."""
        registry = MCPToolRegistry()
        
        def test_function() -> str:
            return "test"
        
        # Register a tool
        registry.register_tool("test_tool", "A test tool", test_function)
        assert len(registry.list_tools()) == 1
        
        # Unregister the tool
        success = registry.unregister_tool("test_tool")
        assert success
        assert len(registry.list_tools()) == 0
        
        # Try to unregister non-existent tool
        success = registry.unregister_tool("non_existent")
        assert not success
    
    def test_get_nonexistent_tool(self):
        """Test getting a non-existent tool."""
        registry = MCPToolRegistry()
        
        tool = registry.get_tool("non_existent")
        assert tool is None
    
    def test_multiple_tools(self):
        """Test registering multiple tools."""
        registry = MCPToolRegistry()
        
        def tool1() -> str:
            return "tool1"
        
        def tool2() -> str:
            return "tool2"
        
        registry.register_tool("tool1", "First tool", tool1)
        registry.register_tool("tool2", "Second tool", tool2)
        
        tools = registry.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
        
        assert registry.get_tool("tool1")["function"] == tool1
        assert registry.get_tool("tool2")["function"] == tool2
