"""Unit tests for enhanced AgentWrapper functionality."""

import json
from unittest.mock import patch

import pytest

from agenthub.core.agents.wrapper import AgentWrapper
from agenthub.core.tools.exceptions import ToolNotFoundError
from agenthub.core.tools.metadata import ToolMetadata
from agenthub.core.tools.registry import ToolRegistry


class TestAgentWrapper:
    """Test cases for enhanced AgentWrapper functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Reset the registry for each test
        ToolRegistry._instance = None
        self.registry = ToolRegistry()

        # Mock agent info
        self.agent_info = {
            "name": "test_agent",
            "path": "/path/to/agent",
            "manifest": {
                "name": "test_agent",
                "description": "Test agent",
                "version": "1.0.0",
                "entry_point": "agent.py",
                "methods": ["run", "analyze", "process"],
            },
        }

        # Mock tool registry
        self.tool_registry = self.registry

        # Patch the global registry to use our test instance
        self.registry_patcher = patch(
            "agenthub.core.tools.registry._registry", self.registry
        )
        self.registry_patcher.start()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "registry_patcher"):
            self.registry_patcher.stop()

    def test_agent_wrapper_initialization_with_tools(self):
        """Test AgentWrapper initialization with tool registry."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        assert wrapper.agent_info == self.agent_info
        assert wrapper.tool_registry == self.tool_registry
        assert wrapper.assigned_tools == []

    def test_agent_wrapper_initialization_without_tools(self):
        """Test AgentWrapper initialization without tool registry."""
        wrapper = AgentWrapper(self.agent_info)

        assert wrapper.agent_info == self.agent_info
        assert wrapper.tool_registry is None
        assert wrapper.assigned_tools == []

    def test_assign_tools(self):
        """Test assigning tools to agent wrapper."""

        # Register some tools
        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        # Assign tools
        wrapper.assign_tools(["tool1", "tool2"])

        assert wrapper.assigned_tools == ["tool1", "tool2"]

    def test_assign_tools_nonexistent(self):
        """Test assigning non-existent tools raises error."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        with pytest.raises(
            ToolNotFoundError
        ):  # Should raise ToolNotFoundError for nonexistent tool
            wrapper.assign_tools(["nonexistent_tool"])

    def test_get_tool_context_json(self):
        """Test getting tool context JSON."""

        # Register some tools
        def tool1(param: str) -> str:
            return f"result: {param}"

        def tool2(param: int) -> int:
            return param * 2

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper.assign_tools(["tool1", "tool2"])

        # Get tool context JSON
        context_json = wrapper.get_tool_context_json()

        # Parse and validate JSON
        context = json.loads(context_json)

        assert "available_tools" in context
        assert "tool_descriptions" in context
        assert "tool_usage_examples" in context
        assert "tool_parameters" in context
        assert "tool_return_types" in context
        assert "tool_namespaces" in context

        # Check specific values
        assert set(context["available_tools"]) == {"tool1", "tool2"}
        assert "tool1" in context["tool_descriptions"]
        assert "tool2" in context["tool_descriptions"]
        assert "tool1" in context["tool_usage_examples"]
        assert "tool2" in context["tool_usage_examples"]

    def test_get_tool_context_json_no_tools(self):
        """Test getting tool context JSON when no tools are assigned."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        context_json = wrapper.get_tool_context_json()
        context = json.loads(context_json)

        assert context["available_tools"] == []
        assert context["tool_descriptions"] == {}
        assert context["tool_usage_examples"] == {}
        assert context["tool_parameters"] == {}
        assert context["tool_return_types"] == {}
        assert context["tool_namespaces"] == {}

    def test_generate_agent_call_json(self):
        """Test generating complete agent call JSON."""

        # Register some tools
        def tool1(param: str) -> str:
            return f"result: {param}"

        self.registry.register_tool("tool1", tool1, "Tool 1")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper.assign_tools(["tool1"])

        # Generate agent call JSON
        call_json = wrapper.generate_agent_call_json(
            method="run", parameters={"text": "Hello world", "analysis_type": "general"}
        )

        # Parse and validate JSON
        call_data = json.loads(call_json)

        assert call_data["method"] == "run"
        assert call_data["parameters"]["text"] == "Hello world"
        assert call_data["parameters"]["analysis_type"] == "general"
        assert "tool_context" in call_data

        # Check tool context
        tool_context = call_data["tool_context"]
        assert "tool1" in tool_context["available_tools"]

    def test_generate_agent_call_json_no_tools(self):
        """Test generating agent call JSON without tools."""
        wrapper = AgentWrapper(self.agent_info)

        call_json = wrapper.generate_agent_call_json(
            method="run", parameters={"text": "Hello world"}
        )

        call_data = json.loads(call_json)

        assert call_data["method"] == "run"
        assert call_data["parameters"]["text"] == "Hello world"
        assert call_data["tool_context"]["available_tools"] == []

    def test_get_tool_instructions(self):
        """Test getting tool instructions for agent."""

        # Register some tools
        def tool1(param: str) -> str:
            """Tool 1 description."""
            return f"result: {param}"

        def tool2(param: int) -> int:
            """Tool 2 description."""
            return param * 2

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper.assign_tools(["tool1", "tool2"])

        instructions = wrapper.get_tool_instructions()

        assert "tool1" in instructions
        assert "tool2" in instructions
        assert "Tool 1" in instructions
        assert "Tool 2" in instructions

    def test_get_tool_instructions_no_tools(self):
        """Test getting tool instructions when no tools are assigned."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        instructions = wrapper.get_tool_instructions()

        assert instructions == ""

    def test_execute_tool(self):
        """Test executing a tool through the wrapper."""

        # Register a tool
        def test_tool(param: str) -> str:
            return f"executed: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        wrapper = AgentWrapper(
            self.agent_info, tool_registry=self.tool_registry, agent_id="test_agent"
        )
        wrapper.assign_tools(["test_tool"])

        # Execute tool
        result = wrapper.execute_tool("test_tool", param="test_value")

        assert result == "executed: test_value"

    def test_execute_tool_not_assigned(self):
        """Test executing a tool that's not assigned to the agent."""

        # Register a tool but don't assign it
        def test_tool(param: str) -> str:
            return f"executed: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        # Don't assign any tools

        with pytest.raises(
            PermissionError
        ):  # Should raise PermissionError for no tool access
            wrapper.execute_tool("test_tool", {"param": "test_value"})

    def test_execute_tool_nonexistent(self):
        """Test executing a non-existent tool."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        with pytest.raises(
            PermissionError
        ):  # Should raise PermissionError for no tool access
            wrapper.execute_tool("nonexistent_tool", {})

    def test_get_available_tools(self):
        """Test getting available tools for the agent."""

        # Register some tools
        def tool1():
            return "tool1"

        def tool2():
            return "tool2"

        self.registry.register_tool("tool1", tool1, "Tool 1")
        self.registry.register_tool("tool2", tool2, "Tool 2")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper.assign_tools(["tool1", "tool2"])

        available_tools = wrapper.get_available_tools()

        assert set(available_tools) == {"tool1", "tool2"}

    def test_get_available_tools_no_tools(self):
        """Test getting available tools when no tools are assigned."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        available_tools = wrapper.get_available_tools()

        assert available_tools == []

    def test_get_tool_metadata(self):
        """Test getting tool metadata."""

        # Register a tool
        def test_tool(param: str) -> str:
            return f"result: {param}"

        self.registry.register_tool("test_tool", test_tool, "Test tool")

        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper.assign_tools(["test_tool"])

        metadata = wrapper.get_tool_metadata("test_tool")

        assert metadata is not None
        assert metadata["name"] == "test_tool"
        assert metadata["description"] == "Test tool"

    def test_get_tool_metadata_nonexistent(self):
        """Test getting metadata for non-existent tool."""
        wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        metadata = wrapper.get_tool_metadata("nonexistent_tool")

        assert metadata is None

    def test_agent_wrapper_with_mcp_tools(self):
        """Test AgentWrapper with MCP-discovered tools."""
        # Mock MCP tool discovery
        with (
            patch.object(self.registry, "get_available_tools") as mock_get_available,
            patch.object(self.registry, "get_tool_metadata") as mock_get_metadata,
        ):

            # Mock MCP tools
            mock_get_available.return_value = ["mcp_tool1", "mcp_tool2"]

            mock_metadata = ToolMetadata(
                name="mcp_tool1",
                description="MCP tool 1",
                function=None,
                namespace="mcp",
            )
            mock_get_metadata.return_value = mock_metadata

            wrapper = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
            wrapper.assign_tools(["mcp_tool1"])

            # Should work with MCP tools
            available_tools = wrapper.get_available_tools()
            assert "mcp_tool1" in available_tools

            metadata = wrapper.get_tool_metadata("mcp_tool1")
            assert metadata is not None
            assert metadata["name"] == "mcp_tool1"
            assert metadata["namespace"] == "mcp"

    def test_agent_wrapper_string_representation(self):
        """Test AgentWrapper string representation."""
        wrapper = AgentWrapper(
            self.agent_info, tool_registry=self.tool_registry, agent_id="test_agent"
        )

        str_repr = str(wrapper)

        assert "AgentWrapper" in str_repr
        assert "unknown/unknown" in str_repr

    def test_agent_wrapper_equality(self):
        """Test AgentWrapper equality comparison."""
        wrapper1 = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)
        wrapper2 = AgentWrapper(self.agent_info, tool_registry=self.tool_registry)

        # AgentWrapper doesn't implement __eq__, so instances are not equal
        # even with the same data (they have different object identity)
        assert wrapper1 != wrapper2

        # Different agent info should also not be equal
        different_info = self.agent_info.copy()
        different_info["name"] = "different_agent"
        wrapper3 = AgentWrapper(different_info, tool_registry=self.tool_registry)

        assert wrapper1 != wrapper3
