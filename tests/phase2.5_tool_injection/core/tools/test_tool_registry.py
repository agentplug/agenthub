"""Unit tests for tool registry functionality."""

import threading
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenthub.core.tools.exceptions import ToolNameConflictError, ToolNotFoundError
from agenthub.core.tools.metadata import ToolMetadata
from agenthub.core.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test cases for ToolRegistry functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Reset the registry for each test
        ToolRegistry._instance = None
        self.registry = ToolRegistry()

        # Patch the global registry to use our test instance
        self.registry_patcher = patch(
            "agenthub.core.tools.registry._registry", self.registry
        )
        self.registry_patcher.start()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "registry_patcher"):
            self.registry_patcher.stop()

    def test_singleton_pattern(self):
        """Test that ToolRegistry implements singleton pattern correctly."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()

        assert registry1 is registry2
        assert ToolRegistry._instance is not None

    def test_register_tool_basic(self):
        """Test basic tool registration."""

        def test_tool(param: str) -> str:
            return f"result: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool description")

        assert "test_tool" in self.registry.get_available_tools()

        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.function == test_tool

    def test_register_tool_with_metadata(self):
        """Test tool registration with custom metadata."""

        def test_tool(param: str) -> str:
            return f"result: {param}"

        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            function=test_tool,
            namespace="custom",
        )

        self.registry.register_tool_with_metadata(metadata)

        assert "test_tool" in self.registry.get_available_tools()

        retrieved_metadata = self.registry.get_tool_metadata("test_tool")
        assert retrieved_metadata.name == "test_tool"
        assert retrieved_metadata.description == "Test tool description"
        assert retrieved_metadata.function == test_tool

    def test_register_tool_name_conflict(self):
        """Test that duplicate tool names raise ToolNameConflictError."""

        def first_tool():
            return "first"

        def second_tool():
            return "second"

        self.registry.register_tool("conflict_tool", first_tool, "First tool")

        with pytest.raises(ToolNameConflictError):
            self.registry.register_tool("conflict_tool", second_tool, "Second tool")

    def test_get_available_tools(self):
        """Test getting list of available tools."""
        # Clear the registry to start fresh
        self.registry.cleanup()

        # Register some tools first
        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        available_tools = self.registry.get_available_tools()
        # Should have built-in tools + 2 registered tools
        assert len(available_tools) >= 2
        assert "tool1" in available_tools
        assert "tool2" in available_tools

    def test_get_tool_metadata_existing(self):
        """Test getting metadata for existing tool."""

        def test_tool(param: str) -> str:
            return f"result: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool description")

        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.function == test_tool

    def test_get_tool_metadata_nonexistent(self):
        """Test getting metadata for non-existent tool."""
        metadata = self.registry.get_tool_metadata("nonexistent_tool")
        assert metadata is None

    def test_assign_tools_to_agent(self):
        """Test assigning tools to agents."""

        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        # Assign tools to agent
        self.registry.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Check assignment
        assert "agent1" in self.registry.agent_tool_access
        assert set(self.registry.agent_tool_access["agent1"]) == {"tool1", "tool2"}

    def test_assign_tools_to_agent_nonexistent_tool(self):
        """Test assigning non-existent tools raises ToolNotFoundError."""
        with pytest.raises(ToolNotFoundError):
            self.registry.assign_tools_to_agent("agent1", ["nonexistent_tool"])

    def test_get_agent_tools(self):
        """Test getting tools assigned to an agent."""

        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        # Assign tools to agent
        self.registry.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Get agent tools
        agent_tools = self.registry.get_agent_tools("agent1")
        assert set(agent_tools) == {"tool1", "tool2"}

    def test_get_agent_tools_nonexistent_agent(self):
        """Test getting tools for non-existent agent returns empty list."""
        agent_tools = self.registry.get_agent_tools("nonexistent_agent")
        assert agent_tools == []

    def test_remove_tool(self):
        """Test removing a tool from registry."""

        def test_tool():
            return "test"

        self.registry.register_tool("test_tool", test_tool, "Test tool")
        assert "test_tool" in self.registry.get_available_tools()

        self.registry.remove_tool("test_tool")
        assert "test_tool" not in self.registry.get_available_tools()

    def test_remove_tool_nonexistent(self):
        """Test removing non-existent tool does nothing."""
        # Should not raise an error
        self.registry.remove_tool("nonexistent_tool")

    def test_clear_agent_tools(self):
        """Test clearing tools for an agent."""

        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        # Assign tools to agent
        self.registry.assign_tools_to_agent("agent1", ["tool1", "tool2"])
        assert len(self.registry.get_agent_tools("agent1")) == 2

        # Clear agent tools
        self.registry.clear_agent_tools("agent1")
        assert len(self.registry.get_agent_tools("agent1")) == 0

    def test_thread_safety(self):
        """Test that registry operations are thread-safe."""
        results = []
        errors = []

        def register_tool(tool_id: int):
            try:

                def tool_func():
                    return f"tool_{tool_id}"

                self.registry.register_tool(
                    f"thread_tool_{tool_id}", tool_func, f"Tool {tool_id}"
                )
                results.append(tool_id)
            except Exception as e:
                errors.append(e)

        # Create multiple threads registering tools simultaneously
        threads = []
        for i in range(20):
            thread = threading.Thread(target=register_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all tools were registered successfully
        assert len(errors) == 0, f"Errors during concurrent registration: {errors}"
        assert len(results) == 20

        # Check that all tools are available
        available_tools = self.registry.get_available_tools()
        # Should have built-in tools + 20 registered tools
        assert len(available_tools) >= 20

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_get_available_tools_with_mcp_discovery(
        self, mock_session_class, mock_sse_client
    ):
        """Test getting available tools with MCP discovery."""
        # Mock MCP client response
        mock_tool1 = MagicMock()
        mock_tool1.name = "mcp_tool1"

        mock_tool2 = MagicMock()
        mock_tool2.name = "mcp_tool2"

        mock_tools = MagicMock()
        mock_tools.tools = [mock_tool1, mock_tool2]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools)

        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_sse_client.return_value.__aenter__.return_value = (
            MagicMock(),
            MagicMock(),
        )

        # Register local tool
        def local_tool():
            return "local"

        self.registry.register_tool("local_tool", local_tool, "Local tool")

        # Get available tools (should include both local and MCP tools)
        available_tools = self.registry.get_available_tools()

        # Should include both local and MCP tools
        assert "local_tool" in available_tools
        assert "mcp_tool1" in available_tools
        assert "mcp_tool2" in available_tools
        assert len(available_tools) == 3

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_get_tool_metadata_with_mcp_discovery(
        self, mock_session_class, mock_sse_client
    ):
        """Test getting tool metadata with MCP discovery."""
        # Mock MCP client response
        mock_tool = MagicMock()
        mock_tool.name = "mcp_tool"
        mock_tool.description = "MCP tool description"

        mock_tools = MagicMock()
        mock_tools.tools = [mock_tool]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools)

        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_sse_client.return_value.__aenter__.return_value = (
            MagicMock(),
            MagicMock(),
        )

        # Get metadata for MCP tool
        metadata = self.registry.get_tool_metadata("mcp_tool")

        assert metadata is not None
        assert metadata.name == "mcp_tool"
        assert metadata.description == "MCP tool description"
        assert metadata.namespace == "mcp"

    def test_assign_tools_to_agent_with_mcp_tools(self):
        """Test assigning tools to agent including MCP-discovered tools."""

        # Register local tool
        def local_tool():
            return "local"

        self.registry.register_tool("local_tool", local_tool, "Local tool")

        # Mock MCP discovery to return additional tools
        with patch.object(self.registry, "get_available_tools") as mock_get_available:
            mock_get_available.return_value = ["local_tool", "mcp_tool1", "mcp_tool2"]

            # Should not raise error when assigning MCP tools
            self.registry.assign_tools_to_agent("agent1", ["local_tool", "mcp_tool1"])

            agent_tools = self.registry.get_agent_tools("agent1")
            assert set(agent_tools) == {"local_tool", "mcp_tool1"}

    def test_registry_cleanup(self):
        """Test registry cleanup functionality."""

        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")
        self.registry.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Cleanup
        self.registry.cleanup()

        # Check that registered tools are cleared
        available_tools = self.registry.get_available_tools()
        # Should not have our registered tools anymore
        assert "tool1" not in available_tools
        assert "tool2" not in available_tools
        assert len(self.registry.agent_tool_access) == 0

    def test_tool_execution_via_registry(self):
        """Test executing tools through registry."""

        def test_tool(param: str) -> str:
            return f"executed: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        # Execute tool
        result = self.registry.execute_tool("test_tool", {"param": "test_value"})
        assert result == "executed: test_value"

    def test_tool_execution_nonexistent_tool(self):
        """Test executing non-existent tool raises ToolNotFoundError."""
        with pytest.raises(ToolNotFoundError):
            self.registry.execute_tool("nonexistent_tool", {})

    def test_tool_execution_with_invalid_parameters(self):
        """Test executing tool with invalid parameters."""

        def test_tool(param: str) -> str:
            return f"executed: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        # Execute with missing required parameter
        with pytest.raises(TypeError):
            self.registry.execute_tool("test_tool", {})

    def test_registry_statistics(self):
        """Test registry statistics functionality."""

        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")
        self.registry.assign_tools_to_agent("agent1", ["tool1"])
        self.registry.assign_tools_to_agent("agent2", ["tool2"])

        stats = self.registry.get_statistics()

        assert stats["total_tools"] == 2
        assert stats["total_agents"] == 2
        assert stats["tools_per_agent"]["agent1"] == 1
        assert stats["tools_per_agent"]["agent2"] == 1
