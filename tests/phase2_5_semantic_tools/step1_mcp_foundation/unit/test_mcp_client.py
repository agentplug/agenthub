"""Unit tests for MCP Client implementation."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from agentmanager.core.mcp import MCPClient, MCPClientManager


class TestMCPClient:
    """Test cases for MCPClient class."""
    
    def test_client_initialization(self):
        """Test MCP client initialization."""
        client = MCPClient(timeout=15.0)
        
        assert client.timeout == 15.0
        assert not client.is_connected()
    
    def test_client_initialization_default_timeout(self):
        """Test MCP client initialization with default timeout."""
        client = MCPClient()
        
        assert client.timeout == 30.0
        assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_client_connect_disconnect(self):
        """Test client connection and disconnection."""
        client = MCPClient()
        
        # Test initial state
        assert not client.is_connected()
        
        # Mock the connection process by directly setting up the client
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.close = AsyncMock()
        
        # Simulate successful connection
        client.session = mock_session
        client.connected = True
        
        assert client.is_connected()
        
        # Test disconnection
        await client.disconnect()
        
        assert not client.is_connected()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing tools from server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_tools_response = Mock()
        mock_tool1 = Mock()
        mock_tool1.name = "tool1"
        mock_tool1.description = "First tool"
        mock_tool1.inputSchema = {"type": "object"}
        
        mock_tool2 = Mock()
        mock_tool2.name = "tool2"
        mock_tool2.description = "Second tool"
        mock_tool2.inputSchema = {"type": "object"}
        
        mock_tools_response.tools = [mock_tool1, mock_tool2]
        mock_session.list_tools.return_value = mock_tools_response
        
        client.session = mock_session
        client.connected = True
        
        tools = await client.list_tools()
        
        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        assert tools[0]["description"] == "First tool"
        assert tools[1]["name"] == "tool2"
        assert tools[1]["description"] == "Second tool"
    
    @pytest.mark.asyncio
    async def test_call_tool(self):
        """Test calling a tool on the server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_content = Mock()
        mock_content.text = "Tool result"
        mock_result.content = [mock_content]
        mock_session.call_tool.return_value = mock_result
        
        client.session = mock_session
        client.connected = True
        
        result = await client.call_tool("test_tool", {"param": "value"})
        
        assert result == "Tool result"
        mock_session.call_tool.assert_called_once_with("test_tool", {"param": "value"})
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing resources from server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_resources_response = Mock()
        mock_resource1 = Mock()
        mock_resource1.uri = "test://resource1"
        mock_resource1.name = "Resource 1"
        mock_resource1.description = "First resource"
        
        mock_resource2 = Mock()
        mock_resource2.uri = "test://resource2"
        mock_resource2.name = "Resource 2"
        mock_resource2.description = "Second resource"
        
        mock_resources_response.resources = [mock_resource1, mock_resource2]
        mock_session.list_resources.return_value = mock_resources_response
        
        client.session = mock_session
        client.connected = True
        
        resources = await client.list_resources()
        
        assert len(resources) == 2
        assert resources[0]["uri"] == "test://resource1"
        assert resources[0]["name"] == "Resource 1"
        assert resources[1]["uri"] == "test://resource2"
        assert resources[1]["name"] == "Resource 2"
    
    @pytest.mark.asyncio
    async def test_read_resource(self):
        """Test reading a resource from server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_content = Mock()
        mock_content.uri = "test://resource"
        mock_content.mimeType = "text/plain"
        mock_content.text = "Resource content"
        mock_result.contents = [mock_content]
        mock_session.read_resource.return_value = mock_result
        
        client.session = mock_session
        client.connected = True
        
        result = await client.read_resource("test://resource")
        
        assert result["uri"] == "test://resource"
        assert len(result["contents"]) == 1
        assert result["contents"][0]["uri"] == "test://resource"
        assert result["contents"][0]["mimeType"] == "text/plain"
        assert result["contents"][0]["text"] == "Resource content"
    
    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Test listing prompts from server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_prompts_response = Mock()
        mock_prompt1 = Mock()
        mock_prompt1.name = "prompt1"
        mock_prompt1.description = "First prompt"
        
        mock_prompt2 = Mock()
        mock_prompt2.name = "prompt2"
        mock_prompt2.description = "Second prompt"
        
        mock_prompts_response.prompts = [mock_prompt1, mock_prompt2]
        mock_session.list_prompts.return_value = mock_prompts_response
        
        client.session = mock_session
        client.connected = True
        
        prompts = await client.list_prompts()
        
        assert len(prompts) == 2
        assert prompts[0]["name"] == "prompt1"
        assert prompts[0]["description"] == "First prompt"
        assert prompts[1]["name"] == "prompt2"
        assert prompts[1]["description"] == "Second prompt"
    
    @pytest.mark.asyncio
    async def test_get_prompt(self):
        """Test getting a prompt from server."""
        client = MCPClient()
        
        # Mock connected client with session
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.description = "Test prompt"
        mock_message = Mock()
        mock_message.role = "user"
        mock_message.content.text = "Test prompt content"
        mock_result.messages = [mock_message]
        mock_session.get_prompt.return_value = mock_result
        
        client.session = mock_session
        client.connected = True
        
        result = await client.get_prompt("test_prompt", {"arg": "value"})
        
        assert result["description"] == "Test prompt"
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"]["text"] == "Test prompt content"
    
    @pytest.mark.asyncio
    async def test_not_connected_error(self):
        """Test that operations fail when not connected."""
        client = MCPClient()
        
        # Test various operations when not connected
        with pytest.raises(Exception, match="Not connected to server"):
            await client.list_tools()
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.call_tool("test", {})
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.list_resources()
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.read_resource("test://resource")
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.list_prompts()
        
        with pytest.raises(Exception, match="Not connected to server"):
            await client.get_prompt("test")
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as async context manager."""
        client = MCPClient()
        
        # Test context manager
        async with client:
            # Simulate connection
            mock_session = AsyncMock()
            mock_session.close = AsyncMock()
            client.session = mock_session
            client.connected = True
            
            assert client.is_connected()
        
        # Should be disconnected after context exit
        assert not client.is_connected()


class TestMCPClientManager:
    """Test cases for MCPClientManager class."""
    
    def test_manager_initialization(self):
        """Test client manager initialization."""
        manager = MCPClientManager()
        
        assert len(manager.list_clients()) == 0
    
    @pytest.mark.asyncio
    async def test_create_client(self):
        """Test creating a client through manager."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            client = await manager.create_client("test_client", ["python", "server.py"])
            
            assert client == mock_client
            assert "test_client" in manager.list_clients()
            mock_client.connect.assert_called_once_with(["python", "server.py"])
    
    @pytest.mark.asyncio
    async def test_create_duplicate_client(self):
        """Test creating a client with duplicate name."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Create first client
            await manager.create_client("test_client", ["python", "server.py"])
            
            # Try to create duplicate
            with pytest.raises(ValueError, match="Client 'test_client' already exists"):
                await manager.create_client("test_client", ["python", "server2.py"])
    
    @pytest.mark.asyncio
    async def test_get_client(self):
        """Test getting a client by name."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Create client
            await manager.create_client("test_client", ["python", "server.py"])
            
            # Get client
            client = await manager.get_client("test_client")
            assert client == mock_client
            
            # Get non-existent client
            client = await manager.get_client("non_existent")
            assert client is None
    
    @pytest.mark.asyncio
    async def test_disconnect_client(self):
        """Test disconnecting a client."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Create client
            await manager.create_client("test_client", ["python", "server.py"])
            assert len(manager.list_clients()) == 1
            
            # Disconnect client
            success = await manager.disconnect_client("test_client")
            assert success
            assert len(manager.list_clients()) == 0
            mock_client.disconnect.assert_called_once()
            
            # Try to disconnect non-existent client
            success = await manager.disconnect_client("non_existent")
            assert not success
    
    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test disconnecting all clients."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client1 = AsyncMock()
            mock_client1.connect = AsyncMock()
            mock_client1.disconnect = AsyncMock()
            
            mock_client2 = AsyncMock()
            mock_client2.connect = AsyncMock()
            mock_client2.disconnect = AsyncMock()
            
            mock_client_class.side_effect = [mock_client1, mock_client2]
            
            # Create multiple clients
            await manager.create_client("client1", ["python", "server1.py"])
            await manager.create_client("client2", ["python", "server2.py"])
            assert len(manager.list_clients()) == 2
            
            # Disconnect all
            await manager.disconnect_all()
            assert len(manager.list_clients()) == 0
            mock_client1.disconnect.assert_called_once()
            mock_client2.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test manager as async context manager."""
        manager = MCPClientManager()
        
        with patch('agentmanager.core.mcp.client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Test context manager
            async with manager:
                await manager.create_client("test_client", ["python", "server.py"])
                assert len(manager.list_clients()) == 1
            
            # Should be disconnected after context exit
            assert len(manager.list_clients()) == 0
            mock_client.disconnect.assert_called_once()
