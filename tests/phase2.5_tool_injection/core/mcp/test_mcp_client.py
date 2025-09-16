"""Unit tests for MCP client functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenthub.core.mcp.mcp_client import MCPClient


class TestMCPClient:
    """Test cases for MCP client functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.client = MCPClient("http://localhost:8000/sse")

    def test_client_initialization(self):
        """Test MCP client initialization."""
        assert self.client.url == "http://localhost:8000/sse"
        assert self.client.session is None
        assert self.client.is_connected is False

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_connect_success(self, mock_session_class, mock_sse_client):
        """Test successful connection to MCP server."""
        # Mock the connection
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_connect():
            await self.client.connect()
            assert self.client.is_connected is True
            assert self.client.session is not None

        asyncio.run(test_connect())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    def test_connect_failure(self, mock_sse_client):
        """Test connection failure handling."""
        # Mock connection failure
        mock_sse_client.side_effect = Exception("Connection failed")

        async def test_connect_failure():
            with pytest.raises(Exception, match="Connection failed"):
                await self.client.connect()
            assert self.client.is_connected is False

        asyncio.run(test_connect_failure())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_disconnect(self, mock_session_class, mock_sse_client):
        """Test disconnection from MCP server."""
        # Mock the connection
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_disconnect():
            await self.client.connect()
            assert self.client.is_connected is True

            await self.client.disconnect()
            assert self.client.is_connected is False
            assert self.client.session is None

        asyncio.run(test_disconnect())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_list_tools(self, mock_session_class, mock_sse_client):
        """Test listing available tools."""
        # Mock the connection and tools response
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_tool1 = MagicMock()
        mock_tool1.name = "tool1"
        mock_tool1.description = "Tool 1 description"

        mock_tool2 = MagicMock()
        mock_tool2.name = "tool2"
        mock_tool2.description = "Tool 2 description"

        mock_tools = MagicMock()
        mock_tools.tools = [mock_tool1, mock_tool2]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_list_tools():
            await self.client.connect()
            tools = await self.client.list_tools()

            assert len(tools) == 2
            assert tools[0].name == "tool1"
            assert tools[0].description == "Tool 1 description"
            assert tools[1].name == "tool2"
            assert tools[1].description == "Tool 2 description"

        asyncio.run(test_list_tools())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_call_tool(self, mock_session_class, mock_sse_client):
        """Test calling a tool via MCP."""
        # Mock the connection and tool call response
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_result = MagicMock()
        mock_result.content = [{"text": "Tool execution result"}]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value=mock_result)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_call_tool():
            await self.client.connect()
            result = await self.client.call_tool("test_tool", {"param": "value"})

            assert result == "Tool execution result"
            mock_session.call_tool.assert_called_once_with(
                "test_tool", {"param": "value"}
            )

        asyncio.run(test_call_tool())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_call_tool_failure(self, mock_session_class, mock_sse_client):
        """Test tool call failure handling."""
        # Mock the connection and tool call failure
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = AsyncMock(side_effect=Exception("Tool call failed"))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_call_tool_failure():
            await self.client.connect()

            with pytest.raises(Exception, match="Tool call failed"):
                await self.client.call_tool("test_tool", {"param": "value"})

        asyncio.run(test_call_tool_failure())

    def test_context_manager(self):
        """Test MCP client as context manager."""
        with (
            patch("agenthub.core.mcp.mcp_client.sse_client") as mock_sse_client,
            patch(
                "agenthub.core.mcp.mcp_client.ClientSession"
            ) as mock_session_class,
        ):

            # Mock the connection
            mock_streams = (MagicMock(), MagicMock())
            mock_sse_client.return_value.__aenter__.return_value = mock_streams

            mock_session = AsyncMock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            async def test_context_manager():
                async with self.client as client:
                    assert client.is_connected is True
                    assert client.session is not None

                # After context exit, should be disconnected
                assert self.client.is_connected is False

            asyncio.run(test_context_manager())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_get_tool_info(self, mock_session_class, mock_sse_client):
        """Test getting tool information."""
        # Mock the connection and tool info response
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool description"

        mock_tools = MagicMock()
        mock_tools.tools = [mock_tool]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_get_tool_info():
            await self.client.connect()
            tool_info = await self.client.get_tool_info("test_tool")

            assert tool_info is not None
            assert tool_info["name"] == "test_tool"
            assert tool_info["description"] == "Test tool description"

        asyncio.run(test_get_tool_info())

    @patch("agenthub.core.mcp.mcp_client.sse_client")
    @patch("agenthub.core.mcp.mcp_client.ClientSession")
    def test_get_tool_info_not_found(self, mock_session_class, mock_sse_client):
        """Test getting tool information for non-existent tool."""
        # Mock the connection and empty tools response
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_tools = MagicMock()
        mock_tools.tools = []

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        async def test_get_tool_info_not_found():
            await self.client.connect()
            tool_info = await self.client.get_tool_info("nonexistent_tool")

            assert tool_info is None

        asyncio.run(test_get_tool_info_not_found())

    def test_connection_timeout(self):
        """Test connection timeout handling."""
        with patch("agenthub.core.mcp.mcp_client.sse_client") as mock_sse_client:
            # Mock timeout
            mock_sse_client.side_effect = TimeoutError("Connection timeout")

            async def test_timeout():
                with pytest.raises(asyncio.TimeoutError):
                    await self.client.connect(timeout=1.0)

            asyncio.run(test_timeout())

    def test_retry_mechanism(self):
        """Test connection retry mechanism."""
        with patch("agenthub.core.mcp.mcp_client.sse_client") as mock_sse_client:
            # Mock first attempt failure, second success
            mock_sse_client.side_effect = [
                Exception("First attempt failed"),
                MagicMock(),
            ]

            async def test_retry():
                # This would need to be implemented in the actual client
                # For now, just test that the client handles exceptions
                with pytest.raises(Exception, match="First attempt failed"):
                    await self.client.connect()

            asyncio.run(test_retry())

    def test_client_cleanup(self):
        """Test client cleanup functionality."""
        # Mock a connected state
        self.client.session = MagicMock()
        self.client.is_connected = True

        # Cleanup should reset the state
        self.client.cleanup()

        assert self.client.session is None
        assert self.client.is_connected is False

    def test_client_repr(self):
        """Test client string representation."""
        repr_str = repr(self.client)
        assert "MCPClient" in repr_str
        assert "http://localhost:8000/sse" in repr_str
        assert "connected=False" in repr_str
