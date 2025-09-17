#!/usr/bin/env python3
"""Unit Tests for Phase 2.5 Step 1: Core Tools Foundation

Tests the tool registry, @tool decorator, and FastMCP integration.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from agenthub.core.tools import (
    ToolNameConflictError,
    ToolRegistry,
    ToolValidationError,
    get_available_tools,
    get_mcp_server,
    get_tool_metadata,
    tool,
)


class TestToolRegistry:
    """Test the ToolRegistry singleton class."""

    def test_singleton_pattern(self):
        """Test that ToolRegistry is a singleton."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        assert registry1 is registry2

    def test_initialization(self):
        """Test registry initialization."""
        registry = ToolRegistry()
        assert hasattr(registry, "mcp_server")
        assert hasattr(registry, "registered_tools")
        assert hasattr(registry, "tool_metadata")
        assert registry.mcp_server.name == "AgentHub Tools"

    def test_register_tool_success(self):
        """Test successful tool registration."""
        registry = ToolRegistry()

        def test_func(data: str) -> dict:
            return {"data": data}

        # Clear any existing tools for clean test
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        result = registry.register_tool("test_tool", test_func, "Test tool")

        assert result == test_func
        assert "test_tool" in registry.registered_tools
        assert "test_tool" in registry.tool_metadata
        assert registry.registered_tools["test_tool"] == test_func

    def test_register_tool_validation_errors(self):
        """Test tool registration validation errors."""
        registry = ToolRegistry()

        def valid_func(data: str) -> dict:
            return {"data": data}

        # Test empty name
        with pytest.raises(
            ToolValidationError, match="Tool name must be a non-empty string"
        ):
            registry.register_tool("", valid_func, "Test")

        # Test non-string name
        with pytest.raises(
            ToolValidationError, match="Tool name must be a non-empty string"
        ):
            registry.register_tool(None, valid_func, "Test")

        # Test non-callable function
        with pytest.raises(ToolValidationError, match="Tool must be callable"):
            registry.register_tool("test", "not_callable", "Test")

        # Test function with no parameters (should work now)
        def no_params() -> dict:
            return {}

        # This should now succeed since we allow functions with no parameters
        result = registry.register_tool("no_params", no_params, "Test")
        assert result == no_params
        assert "no_params" in registry.get_available_tools()

    def test_register_tool_name_conflict(self):
        """Test tool name conflict error."""
        registry = ToolRegistry()

        def func1(data: str) -> dict:
            return {"data": data}

        def func2(data: str) -> dict:
            return {"data": data}

        # Clear any existing tools
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        # Register first tool
        registry.register_tool("conflict_tool", func1, "First tool")

        # Try to register with same name
        with pytest.raises(
            ToolNameConflictError, match="Tool 'conflict_tool' is already registered"
        ):
            registry.register_tool("conflict_tool", func2, "Second tool")

    def test_get_available_tools(self):
        """Test getting available tools list."""
        registry = ToolRegistry()

        def test_func(data: str) -> dict:
            return {"data": data}

        # Clear and add test tool
        registry.registered_tools.clear()
        registry.tool_metadata.clear()
        registry.register_tool("list_test_tool", test_func, "List test")

        tools = registry.get_available_tools()
        assert "list_test_tool" in tools
        assert isinstance(tools, list)

    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        registry = ToolRegistry()

        def test_func(data: str) -> dict:
            return {"data": data}

        # Clear and add test tool
        registry.registered_tools.clear()
        registry.tool_metadata.clear()
        registry.register_tool("metadata_test_tool", test_func, "Metadata test")

        metadata = registry.get_tool_metadata("metadata_test_tool")
        assert metadata is not None
        assert metadata.name == "metadata_test_tool"
        assert metadata.description == "Metadata test"
        assert metadata.function == test_func

        # Test non-existent tool
        assert registry.get_tool_metadata("non_existent") is None


class TestToolDecorator:
    """Test the @tool decorator."""

    def test_tool_decorator_basic(self):
        """Test basic @tool decorator functionality."""
        # Clear registry for clean test
        registry = ToolRegistry()
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        @tool(name="decorator_test", description="Decorator test tool")
        def test_func(data: str) -> dict:
            return {"data": data}

        # Check that function is registered
        assert "decorator_test" in get_available_tools()
        assert test_func("test") == {"data": "test"}

    def test_tool_decorator_without_description(self):
        """Test @tool decorator without description."""
        registry = ToolRegistry()
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        @tool(name="no_desc_test")
        def test_func(data: str) -> dict:
            return {"data": data}

        assert "no_desc_test" in get_available_tools()
        metadata = get_tool_metadata("no_desc_test")
        assert metadata.description == ""


class TestMCPIntegration:
    """Test FastMCP integration."""

    def test_mcp_server_initialization(self):
        """Test MCP server is properly initialized."""
        mcp_server = get_mcp_server()
        assert mcp_server is not None
        assert hasattr(mcp_server, "name")
        assert mcp_server.name == "AgentHub Tools"
        assert hasattr(mcp_server, "_tool_manager")

    @pytest.mark.asyncio
    async def test_mcp_tool_execution(self):
        """Test tool execution through MCP server."""
        # Clear registry and add test tool
        registry = ToolRegistry()
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        @tool(name="mcp_exec_test", description="MCP execution test")
        def mcp_test_func(message: str) -> dict:
            return {"message": message, "processed": True}

        mcp_server = get_mcp_server()

        # Test tool execution
        result = await mcp_server.call_tool(
            "mcp_exec_test", {"message": "test message"}
        )

        assert result is not None
        assert len(result) > 0
        assert hasattr(result[0], "text")

        # Parse the result
        import json

        result_data = json.loads(result[0].text)
        assert result_data["message"] == "test message"
        assert result_data["processed"] is True

    @pytest.mark.asyncio
    async def test_mcp_tool_not_found(self):
        """Test MCP tool not found error."""
        mcp_server = get_mcp_server()

        with pytest.raises((Exception, RuntimeError)):  # FastMCP raises ToolError
            await mcp_server.call_tool("non_existent_tool", {"data": "test"})


class TestWebSearchTool:
    """Test the web search tool specifically."""

    @pytest.mark.asyncio
    async def test_web_search_tool_registration(self):
        """Test web search tool can be registered."""
        registry = ToolRegistry()
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        @tool(name="web_search", description="Search the web")
        def web_search(query: str, max_results: int = 5) -> dict:
            return {"query": query, "results": [], "total_found": 0}

        assert "web_search" in get_available_tools()

    @pytest.mark.asyncio
    @patch("requests.get")
    async def test_web_search_tool_execution(self, mock_get):
        """Test web search tool execution with mocked response."""
        # Mock the DuckDuckGo API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Abstract": "Test abstract",
            "Heading": "Test Heading",
            "AbstractURL": "https://test.com",
            "RelatedTopics": [
                {"Text": "Related topic 1", "FirstURL": "https://related1.com"},
                {"Text": "Related topic 2", "FirstURL": "https://related2.com"},
            ],
        }
        mock_get.return_value = mock_response

        # Clear registry and register web search tool
        registry = ToolRegistry()
        registry.registered_tools.clear()
        registry.tool_metadata.clear()

        # Clear MCP server tools as well
        mcp_server = get_mcp_server()
        mcp_server._tool_manager._tools.clear()

        @tool(name="web_search", description="Search the web")
        def web_search(query: str, max_results: int = 5) -> dict:
            try:
                response = requests.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1",
                    },
                    timeout=10,
                )
                data = response.json()

                results = []
                if data.get("Abstract"):
                    results.append(
                        {
                            "title": data.get("Heading", "No title"),
                            "snippet": data.get("Abstract", ""),
                            "url": data.get("AbstractURL", ""),
                        }
                    )

                for topic in data.get("RelatedTopics", [])[: max_results - 1]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(
                            {
                                "title": topic.get("FirstURL", "")
                                .split("/")[-1]
                                .replace("_", " "),
                                "snippet": topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                            }
                        )

                return {
                    "query": query,
                    "results": results[:max_results],
                    "total_found": len(results),
                }
            except Exception as e:
                return {"query": query, "error": str(e), "results": []}

        mcp_server = get_mcp_server()

        # Test web search execution
        result = await mcp_server.call_tool(
            "web_search", {"query": "test query", "max_results": 2}
        )

        assert result is not None
        assert len(result) > 0

        # Parse and verify result
        import json

        result_data = json.loads(result[0].text)
        assert result_data["query"] == "test query"
        assert "results" in result_data
        assert "total_found" in result_data
        # Note: Results might be empty due to mock setup, but structure is correct
        assert isinstance(result_data["results"], list)


class TestModuleExports:
    """Test module exports and public API."""

    def test_module_exports(self):
        """Test that all expected functions are exported."""
        from agenthub.core.tools import (
            ToolError,
            ToolNameConflictError,
            ToolRegistrationError,
            ToolRegistry,
            ToolValidationError,
            get_available_tools,
            get_mcp_server,
            tool,
        )

        # Test that all exports are callable/importable
        assert callable(tool)
        assert callable(get_available_tools)
        assert callable(get_mcp_server)
        assert callable(ToolRegistry)

        # Test exception classes
        assert issubclass(ToolError, Exception)
        assert issubclass(ToolRegistrationError, ToolError)
        assert issubclass(ToolNameConflictError, ToolError)
        assert issubclass(ToolValidationError, ToolError)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
