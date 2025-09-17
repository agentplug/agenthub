"""Simple tests for Phase 2.5 tool injection functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenthub.core.tools.exceptions import ToolNameConflictError, ToolValidationError
from agenthub.core.tools.registry import ToolRegistry


class TestSimpleToolInjection:
    """Simple test cases for tool injection functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Reset the registry for each test
        ToolRegistry._instance = None
        self.registry = ToolRegistry()

        # Import the global registry for decorator tests
        from agenthub.core.tools.registry import _registry

        self.global_registry = _registry
        # Clean up any existing tools from previous tests
        self.global_registry.cleanup()

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_tool_registration_basic(self, mock_session_class, mock_sse_client):
        """Test basic tool registration."""
        # Mock MCP discovery to return empty list
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Register a tool
        def test_tool(param: str) -> str:
            return f"result: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool description")

        # Check that tool is registered
        assert "test_tool" in self.registry.get_available_tools()

        # Check tool metadata
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.function == test_tool

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_tool_execution(self, mock_session_class, mock_sse_client):
        """Test tool execution."""
        # Mock MCP discovery to return empty list
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Register a tool
        def test_tool(param: str) -> str:
            return f"executed: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        # Get tool function and execute it
        tool_func = self.registry.get_tool_function("test_tool")
        assert tool_func is not None
        result = tool_func("test_value")
        assert result == "executed: test_value"

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_tool_name_conflict(self, mock_session_class, mock_sse_client):
        """Test tool name conflict handling."""
        # Mock MCP discovery to return empty list
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        def first_tool(param: str) -> str:
            return f"first: {param}"

        def second_tool(param: str) -> str:
            return f"second: {param}"

        # Register first tool
        self.registry.register_tool("conflict_tool", first_tool, "First tool")

        # Try to register second tool with same name
        with pytest.raises(ToolNameConflictError):
            self.registry.register_tool("conflict_tool", second_tool, "Second tool")

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_agent_tool_assignment(self, mock_session_class, mock_sse_client):
        """Test agent tool assignment."""
        # Mock MCP discovery to return empty list
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Register tools
        def tool1(param: str) -> str:
            return f"tool1: {param}"

        def tool2(param: str) -> str:
            return f"tool2: {param}"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        # Assign tools to agent
        self.registry.assign_tools_to_agent("test_agent", ["tool1", "tool2"])

        # Check assignment
        agent_tools = self.registry.get_agent_tools("test_agent")
        assert set(agent_tools) == {"tool1", "tool2"}

    def test_tool_validation_errors(self):
        """Test tool validation error handling."""
        # Test with None function
        with pytest.raises(ToolValidationError):
            self.registry.register_tool("none_tool", None, "None function")

        # Test with non-callable
        with pytest.raises(ToolValidationError):
            self.registry.register_tool("non_callable_tool", 42, "Non-callable")

        # Test with empty name
        def test_tool(param: str) -> str:
            return f"test: {param}"

        with pytest.raises(ToolValidationError):
            self.registry.register_tool("", test_tool, "Empty name")

    def test_tool_metadata_creation(self):
        """Test tool metadata creation."""
        from agenthub.core.tools.metadata import ToolMetadata

        def test_tool(param: str) -> str:
            return f"test: {param}"

        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool",
            function=test_tool,
            namespace="custom",
        )

        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool"
        assert metadata.function == test_tool
        assert metadata.namespace == "custom"
        assert metadata.parameters is not None
        assert metadata.return_type is not None
        assert metadata.examples is not None

    def test_tool_metadata_with_none_function(self):
        """Test tool metadata with None function (for MCP tools)."""
        from agenthub.core.tools.metadata import ToolMetadata

        metadata = ToolMetadata(
            name="mcp_tool", description="MCP tool", function=None, namespace="mcp"
        )

        assert metadata.name == "mcp_tool"
        assert metadata.description == "MCP tool"
        assert metadata.function is None
        assert metadata.namespace == "mcp"
        assert metadata.parameters == {}
        assert metadata.return_type == "Any"
        assert len(metadata.examples) > 0
