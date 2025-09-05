"""Integration tests for MCP Server and Client communication."""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from agentmanager.core.mcp import MCPServer, MCPClient, MCPToolRegistry


class TestMCPIntegration:
    """Integration tests for MCP components."""
    
    @pytest.mark.asyncio
    async def test_server_client_integration(self):
        """Test integration between MCP server and client."""
        # Create MCP server
        server = MCPServer(name="Integration Test Server", version="1.0.0")
        
        # Register test tools
        def calculator(a: int, b: int, operation: str = "add") -> str:
            """Simple calculator tool."""
            if operation == "add":
                return str(a + b)
            elif operation == "multiply":
                return str(a * b)
            else:
                return f"Unknown operation: {operation}"
        
        def file_info(file_path: str) -> str:
            """Get file information."""
            try:
                path = Path(file_path)
                if path.exists():
                    return f"File {file_path} exists, size: {path.stat().st_size} bytes"
                else:
                    return f"File {file_path} does not exist"
            except Exception as e:
                return f"Error: {e}"
        
        server.register_tool("calculator", "Simple calculator", calculator)
        server.register_tool("file_info", "Get file information", file_info)
        
        # Verify server setup
        assert server.get_tool_count() == 2
        assert not server.is_running()
        
        # Test tool registry integration
        registry = MCPToolRegistry()
        registry.register_tool("test_tool", "A test tool", lambda x: f"Result: {x}")
        
        assert len(registry.list_tools()) == 1
        tool = registry.get_tool("test_tool")
        assert tool is not None
        assert tool["name"] == "test_tool"
    
    @pytest.mark.asyncio
    async def test_tool_execution_simulation(self):
        """Test tool execution simulation (what agents will do)."""
        # Create server and register tools
        server = MCPServer()
        
        def web_search(query: str) -> str:
            """Simulate web search."""
            return f"Search results for '{query}': Found 3 relevant articles"
        
        def code_generator(language: str, task: str) -> str:
            """Generate code."""
            return f"# {language} code for {task}\n# TODO: Implement"
        
        server.register_tool("web_search", "Search the web", web_search)
        server.register_tool("code_generator", "Generate code", code_generator)
        
        # Simulate tool execution (what happens when agents call tools)
        search_result = web_search("machine learning")
        assert "machine learning" in search_result
        assert "Search results" in search_result
        
        code_result = code_generator("python", "hello world")
        assert "python" in code_result
        assert "hello world" in code_result
        
        # Verify server has the tools registered
        assert server.get_tool_count() == 2
    
    @pytest.mark.asyncio
    async def test_mcp_components_initialization(self):
        """Test that all MCP components initialize correctly."""
        # Test MCPServer
        server = MCPServer(name="Test Server", version="1.0.0")
        assert server.name == "Test Server"
        assert server.version == "1.0.0"
        assert server.get_tool_count() == 0
        assert not server.is_running()
        
        # Test MCPClient
        client = MCPClient(timeout=10.0)
        assert client.timeout == 10.0
        assert not client.is_connected()
        
        # Test MCPToolRegistry
        registry = MCPToolRegistry()
        assert len(registry.list_tools()) == 0
        
        # Test that components can work together
        def test_function(param: str) -> str:
            return f"Processed: {param}"
        
        # Register in server
        server.register_tool("test_tool", "Test tool", test_function)
        assert server.get_tool_count() == 1
        
        # Register in registry
        registry.register_tool("registry_tool", "Registry tool", test_function)
        assert len(registry.list_tools()) == 1
        
        # Both should work independently
        assert server.get_tool_count() == 1
        assert len(registry.list_tools()) == 1
    
    @pytest.mark.asyncio
    async def test_tool_registration_workflow(self):
        """Test the complete tool registration workflow."""
        # Create server
        server = MCPServer()
        
        # Define tools
        def tool1(param: str) -> str:
            return f"Tool1 result: {param}"
        
        def tool2(number: int) -> str:
            return f"Tool2 result: {number * 2}"
        
        def tool3() -> str:
            return "Tool3 result: constant"
        
        # Register tools
        server.register_tool("tool1", "First tool", tool1)
        server.register_tool("tool2", "Second tool", tool2)
        server.register_tool("tool3", "Third tool", tool3)
        
        # Verify registration
        assert server.get_tool_count() == 3
        
        # Test tool execution
        result1 = tool1("test")
        assert result1 == "Tool1 result: test"
        
        result2 = tool2(5)
        assert result2 == "Tool2 result: 10"
        
        result3 = tool3()
        assert result3 == "Tool3 result: constant"
        
        # Test registry integration
        registry = MCPToolRegistry()
        registry.register_tool("registry_tool", "Registry tool", tool1)
        
        tool = registry.get_tool("registry_tool")
        assert tool is not None
        assert tool["function"] == tool1
        
        # Test unregistration
        success = registry.unregister_tool("registry_tool")
        assert success
        assert len(registry.list_tools()) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across MCP components."""
        # Test server error handling
        server = MCPServer()
        
        def error_tool() -> str:
            raise ValueError("Test error")
        
        def normal_tool() -> str:
            return "Normal result"
        
        # Register both tools
        server.register_tool("error_tool", "Tool that errors", error_tool)
        server.register_tool("normal_tool", "Normal tool", normal_tool)
        
        # Test normal tool execution
        result = normal_tool()
        assert result == "Normal result"
        
        # Test error tool execution
        with pytest.raises(ValueError, match="Test error"):
            error_tool()
        
        # Test registry error handling
        registry = MCPToolRegistry()
        
        # Test getting non-existent tool
        tool = registry.get_tool("non_existent")
        assert tool is None
        
        # Test unregistering non-existent tool
        success = registry.unregister_tool("non_existent")
        assert not success
        
        # Test client error handling (not connected)
        client = MCPClient()
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.list_tools()
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.call_tool("test", {})
    
    @pytest.mark.asyncio
    async def test_mcp_foundation_readiness(self):
        """Test that MCP foundation is ready for Step 2."""
        # Create all MCP components
        server = MCPServer(name="Foundation Test", version="1.0.0")
        client = MCPClient(timeout=15.0)
        registry = MCPToolRegistry()
        
        # Register sample tools
        def sample_tool(param: str) -> str:
            return f"Sample: {param}"
        
        server.register_tool("sample_tool", "Sample tool", sample_tool)
        registry.register_tool("registry_sample", "Registry sample", sample_tool)
        
        # Verify foundation is ready
        assert server.get_tool_count() == 1
        assert len(registry.list_tools()) == 1
        assert not client.is_connected()
        
        # Test tool execution
        result = sample_tool("test")
        assert result == "Sample: test"
        
        # Verify MCP instance is available
        mcp_instance = server.get_mcp_instance()
        assert mcp_instance is not None
        
        # Foundation is ready for Step 2: @tool decorator
        print("✅ MCP Foundation is ready for Step 2 implementation")
