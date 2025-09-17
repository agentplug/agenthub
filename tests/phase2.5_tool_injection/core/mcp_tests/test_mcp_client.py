"""Unit tests for MCP client functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenthub.core.mcp.mcp_client import MCPClient


class TestMCPClient:
    """Test cases for MCP client functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.client = MCPClient()

    def test_client_initialization(self):
        """Test MCP client initialization."""
        assert self.client.tool_registry is not None
        assert self.client.client is None
        assert self.client._lock is not None

    @patch("agenthub.core.mcp.mcp_client.stdio_client")
    @patch("agenthub.core.mcp.mcp_client.StdioServerParameters")
    def test_connect_success(self, mock_params_class, mock_stdio_client):
        """Test successful connection to MCP server."""
        # Mock the stdio client and server parameters
        mock_params = MagicMock()
        mock_params_class.return_value = mock_params

        mock_transport = AsyncMock()
        mock_client_session = AsyncMock()
        mock_transport.__aenter__.return_value = mock_client_session
        mock_stdio_client.return_value = mock_transport

        # Test connection
        async def run_test():
            result = await self.client.connect()
            assert result == mock_client_session
            assert self.client.client == mock_client_session

        asyncio.run(run_test())

    @patch("agenthub.core.mcp.mcp_client.stdio_client")
    @patch("agenthub.core.mcp.mcp_client.StdioServerParameters")
    def test_connect_failure(self, mock_params_class, mock_stdio_client):
        """Test connection failure handling."""
        # Mock connection failure
        mock_params = MagicMock()
        mock_params_class.return_value = mock_params

        mock_transport = AsyncMock()
        mock_transport.__aenter__.side_effect = Exception("Connection failed")
        mock_stdio_client.return_value = mock_transport

        # Test connection failure
        async def run_test():
            with pytest.raises(Exception, match="Connection failed"):
                await self.client.connect()

        asyncio.run(run_test())

    def test_disconnect(self):
        """Test disconnecting from MCP server."""
        # Mock client session
        mock_client = AsyncMock()
        self.client.client = mock_client

        # Test disconnect
        async def run_test():
            await self.client.close()
            mock_client.close.assert_called_once()
            assert self.client.client is None

        asyncio.run(run_test())

    def test_list_tools(self):
        """Test listing available tools."""
        # Mock tool registry
        mock_tools = ["tool1", "tool2", "tool3"]
        self.client.tool_registry.get_available_tools = MagicMock(
            return_value=mock_tools
        )

        # Test list tools
        async def run_test():
            result = await self.client.list_tools()
            assert result == mock_tools
            self.client.tool_registry.get_available_tools.assert_called_once()

        asyncio.run(run_test())

    @patch("agenthub.core.mcp.connection_manager.get_connection_pool")
    def test_execute_tool_success(self, mock_get_pool):
        """Test successful tool execution."""
        # Mock connection pool and client
        mock_pool = MagicMock()
        mock_connection = AsyncMock()
        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.text = '{"result": "success"}'
        mock_client.call_tool.return_value = [mock_result]

        mock_connection.__aenter__.return_value = mock_client
        mock_pool.get_connection.return_value = mock_connection
        mock_get_pool.return_value = mock_pool

        # Test tool execution
        async def run_test():
            result = await self.client.execute_tool("test_tool", {"param": "value"})
            assert result == '{"result": "success"}'
            mock_client.call_tool.assert_called_once_with(
                "test_tool", {"param": "value"}
            )

        asyncio.run(run_test())

    @patch("agenthub.core.mcp.connection_manager.get_connection_pool")
    def test_execute_tool_failure(self, mock_get_pool):
        """Test tool execution failure."""
        # Mock connection pool to raise exception
        mock_pool = MagicMock()
        mock_connection = AsyncMock()
        mock_connection.__aenter__.side_effect = Exception("Tool execution failed")
        mock_pool.get_connection.return_value = mock_connection
        mock_get_pool.return_value = mock_pool

        # Test tool execution failure
        async def run_test():
            result = await self.client.execute_tool("test_tool", {"param": "value"})
            assert "error" in result
            assert "Tool execution failed" in result

        asyncio.run(run_test())

    def test_client_repr(self):
        """Test client string representation."""
        repr_str = repr(self.client)
        assert "MCPClient" in repr_str

    def test_client_cleanup(self):
        """Test client cleanup."""
        # Mock client session
        mock_client = AsyncMock()
        self.client.client = mock_client

        # Test cleanup
        async def run_test():
            await self.client.close()
            mock_client.close.assert_called_once()
            assert self.client.client is None

        asyncio.run(run_test())

    def test_connection_lock(self):
        """Test that connection uses proper locking."""
        # This test verifies that the _lock attribute exists and is an asyncio.Lock
        assert isinstance(self.client._lock, asyncio.Lock)

    @patch("agenthub.core.mcp.mcp_client.stdio_client")
    @patch("agenthub.core.mcp.mcp_client.StdioServerParameters")
    def test_multiple_connect_calls(self, mock_params_class, mock_stdio_client):
        """Test that multiple connect calls reuse the same connection."""
        # Mock the stdio client and server parameters
        mock_params = MagicMock()
        mock_params_class.return_value = mock_params

        mock_transport = AsyncMock()
        mock_client_session = AsyncMock()
        mock_transport.__aenter__.return_value = mock_client_session
        mock_stdio_client.return_value = mock_transport

        # Test multiple connections
        async def run_test():
            # First connection
            result1 = await self.client.connect()
            assert result1 == mock_client_session

            # Second connection should reuse the same client
            result2 = await self.client.connect()
            assert result2 == mock_client_session
            assert result1 is result2

            # Should only create one connection
            assert mock_stdio_client.call_count == 1

        asyncio.run(run_test())

    def test_tool_registry_integration(self):
        """Test that MCP client properly integrates with tool registry."""
        assert self.client.tool_registry is not None
        # Verify that list_tools uses the tool registry
        available_tools = self.client.tool_registry.get_available_tools()
        assert isinstance(available_tools, list)
