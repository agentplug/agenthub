"""Unit tests for unified AgentToolManager with Phase 3 features."""

from unittest.mock import MagicMock

import pytest

from agenthub.core.mcp.agent_tool_manager import AgentToolManager
from agenthub.core.tools.exceptions import ToolConflictError, ToolNotFoundError
from agenthub.core.tools.tool_access import ToolAccessManager


def make_registry(available):
    """Mock registry whose assignment store behaves like the real one.

    AgentToolManager delegates assignment storage to the registry's
    access manager (single store); a bare MagicMock swallows those calls,
    so these tests wire a real ToolAccessManager behind the mock.
    """
    registry = MagicMock()
    registry.get_available_tools.return_value = available
    registry.access_manager = ToolAccessManager()
    registry.assign_tools_to_agent.side_effect = (
        lambda agent_id, names: registry.access_manager.assign_tools(
            agent_id, names, available
        )
    )
    return registry


class TestUnifiedAgentToolManager:
    """Test cases for unified AgentToolManager functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Mock agent manifest with built-in tools
        self.manifest = {
            "builtin_tools": {
                "text_analyzer": {
                    "description": "Analyze text content",
                    "required": True,
                    "parameters": {
                        "text": {"type": "string", "required": True},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["sentiment", "entities"],
                        },
                    },
                },
                "keyword_extraction": {
                    "description": "Extract keywords",
                    "required": False,
                    "parameters": {
                        "text": {"type": "string", "required": True},
                        "max_keywords": {"type": "integer", "default": 10},
                    },
                },
            }
        }

    def test_initialization_with_manifest(self):
        """Test AgentToolManager initialization with manifest."""
        tool_manager = AgentToolManager(self.manifest)

        # Check that built-in tools are loaded
        assert len(tool_manager.builtin_tools) == 2
        assert "text_analyzer" in tool_manager.builtin_tools
        assert "keyword_extraction" in tool_manager.builtin_tools

        # Check tool properties
        text_analyzer = tool_manager.builtin_tools["text_analyzer"]
        assert text_analyzer.description == "Analyze text content"
        assert text_analyzer.required is True
        assert text_analyzer.enabled is True

        keyword_tool = tool_manager.builtin_tools["keyword_extraction"]
        assert keyword_tool.description == "Extract keywords"
        assert keyword_tool.required is False
        assert keyword_tool.enabled is True

    def test_initialization_without_manifest(self):
        """Test AgentToolManager initialization without manifest."""
        tool_manager = AgentToolManager()

        # Should have no built-in tools
        assert len(tool_manager.builtin_tools) == 0
        assert len(tool_manager.disabled_tools) == 0

    def test_disable_builtin_tools(self):
        """Test disabling built-in tools."""
        tool_manager = AgentToolManager(self.manifest)

        # Disable optional tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])

        # Check that tool is disabled
        assert not tool_manager.builtin_tools["keyword_extraction"].enabled
        assert "keyword_extraction" in tool_manager.disabled_tools

        # Required tool should still be enabled
        assert tool_manager.builtin_tools["text_analyzer"].enabled

    def test_disable_required_builtin_tool(self):
        """Test that required built-in tools cannot be disabled."""
        tool_manager = AgentToolManager(self.manifest)

        # Try to disable required tool
        with pytest.raises(ValueError, match="cannot be disabled"):
            tool_manager.disable_builtin_tools(["text_analyzer"])

    def test_enable_builtin_tools(self):
        """Test enabling built-in tools."""
        tool_manager = AgentToolManager(self.manifest)

        # First disable a tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])
        assert not tool_manager.builtin_tools["keyword_extraction"].enabled

        # Then enable it
        tool_manager.enable_builtin_tools(["keyword_extraction"])
        assert tool_manager.builtin_tools["keyword_extraction"].enabled
        assert "keyword_extraction" not in tool_manager.disabled_tools

    def test_get_available_builtin_tools(self):
        """Test getting available built-in tools."""
        tool_manager = AgentToolManager(self.manifest)

        # Initially all tools are available
        available = tool_manager.get_available_builtin_tools()
        assert len(available) == 2
        assert "text_analyzer" in available
        assert "keyword_extraction" in available

        # Disable one tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])
        available = tool_manager.get_available_builtin_tools()
        assert len(available) == 1
        assert "text_analyzer" in available
        assert "keyword_extraction" not in available

    def test_is_builtin_tool_available(self):
        """Test checking if built-in tool is available."""
        tool_manager = AgentToolManager(self.manifest)

        # Initially available
        assert tool_manager.is_builtin_tool_available("text_analyzer")
        assert tool_manager.is_builtin_tool_available("keyword_extraction")

        # Disable one tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])
        assert tool_manager.is_builtin_tool_available("text_analyzer")
        assert not tool_manager.is_builtin_tool_available("keyword_extraction")

        # Non-existent tool
        assert not tool_manager.is_builtin_tool_available("nonexistent_tool")

    def test_is_builtin_tool_required(self):
        """Test checking if built-in tool is required."""
        tool_manager = AgentToolManager(self.manifest)

        assert tool_manager.is_builtin_tool_required("text_analyzer")
        assert not tool_manager.is_builtin_tool_required("keyword_extraction")
        assert not tool_manager.is_builtin_tool_required("nonexistent_tool")

    def test_validate_builtin_tool_parameters(self):
        """Test validating built-in tool parameters."""
        tool_manager = AgentToolManager(self.manifest)

        # Valid parameters
        errors = tool_manager.validate_builtin_tool_parameters(
            "text_analyzer", {"text": "Hello world", "analysis_type": "sentiment"}
        )
        assert len(errors) == 0

        # Missing required parameter
        errors = tool_manager.validate_builtin_tool_parameters(
            "text_analyzer", {"analysis_type": "sentiment"}
        )
        assert len(errors) == 1
        assert "Required parameter 'text' is missing" in errors[0]

        # Invalid enum value
        errors = tool_manager.validate_builtin_tool_parameters(
            "text_analyzer", {"text": "Hello world", "analysis_type": "invalid"}
        )
        assert len(errors) == 1
        assert "must be one of" in errors[0]

        # Wrong parameter type
        errors = tool_manager.validate_builtin_tool_parameters(
            "keyword_extraction", {"text": "Hello world", "max_keywords": "ten"}
        )
        assert len(errors) == 1
        assert "should be integer" in errors[0]

    def test_assign_tools_to_agent(self):
        """Test assigning external tools to agent."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2", "tool3"])
        tool_manager.tool_registry = mock_registry

        # Assign tools
        assigned = tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])
        assert assigned == ["tool1", "tool2"]
        assert set(mock_registry.access_manager.get_agent_tools("agent1")) == {
            "tool1",
            "tool2",
        }

    def test_assign_tools_to_agent_conflict_with_builtin(self):
        """Test that external tools cannot conflict with built-in tools."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry
        mock_registry = MagicMock()
        mock_registry.get_available_tools.return_value = ["text_analyzer", "tool1"]
        tool_manager.tool_registry = mock_registry

        # Try to assign tool with same name as built-in
        with pytest.raises(ToolConflictError, match="conflicts with built-in tool"):
            tool_manager.assign_tools_to_agent("agent1", ["text_analyzer"])

    def test_assign_tools_to_agent_nonexistent(self):
        """Test assigning non-existent external tools."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2"])
        tool_manager.tool_registry = mock_registry

        # Try to assign non-existent tool
        with pytest.raises(ToolNotFoundError, match="not found in registry"):
            tool_manager.assign_tools_to_agent("agent1", ["nonexistent_tool"])

    def test_get_agent_tools(self):
        """Test getting tools assigned to an agent."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2"])
        tool_manager.tool_registry = mock_registry

        # Assign tools
        tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Get agent tools
        tools = tool_manager.get_agent_tools("agent1")
        assert set(tools) == {"tool1", "tool2"}

        # Non-existent agent
        tools = tool_manager.get_agent_tools("nonexistent_agent")
        assert tools == []

    def test_get_all_available_tools(self):
        """Test getting all available tools for an agent."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2"])
        tool_manager.tool_registry = mock_registry

        # Assign external tools
        tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Get all available tools
        all_tools = tool_manager.get_all_available_tools("agent1")

        # Should include both built-in and external tools
        assert "text_analyzer" in all_tools  # Built-in
        assert "keyword_extraction" in all_tools  # Built-in
        assert "tool1" in all_tools  # External
        assert "tool2" in all_tools  # External

    def test_has_tool_access(self):
        """Test checking if agent has access to a tool."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1"])
        tool_manager.tool_registry = mock_registry

        # Assign external tools
        tool_manager.assign_tools_to_agent("agent1", ["tool1"])

        # Check access
        assert tool_manager.has_tool_access("agent1", "text_analyzer")  # Built-in
        assert tool_manager.has_tool_access("agent1", "tool1")  # External
        assert not tool_manager.has_tool_access("agent1", "nonexistent_tool")

        # Disable built-in tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])
        assert not tool_manager.has_tool_access("agent1", "keyword_extraction")

    def test_get_tool_summary(self):
        """Test getting comprehensive tool summary."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2"])
        tool_manager.tool_registry = mock_registry

        # Assign external tools
        tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])

        # Disable one built-in tool
        tool_manager.disable_builtin_tools(["keyword_extraction"])

        # Get summary
        summary = tool_manager.get_tool_summary("agent1")

        # Check built-in tools section
        assert summary["builtin_tools"]["total"] == 2
        assert summary["builtin_tools"]["enabled"] == 1
        assert summary["builtin_tools"]["disabled"] == 1
        assert summary["builtin_tools"]["required"] == 1
        assert summary["builtin_tools"]["optional"] == 1
        assert "text_analyzer" in summary["builtin_tools"]["names"]
        assert "keyword_extraction" in summary["builtin_tools"]["names"]
        assert "text_analyzer" in summary["builtin_tools"]["enabled_names"]
        assert "keyword_extraction" in summary["builtin_tools"]["disabled_names"]

        # Check external tools section
        assert summary["external_tools"]["count"] == 2
        assert set(summary["external_tools"]["names"]) == {"tool1", "tool2"}

        # Check all available tools
        all_available = summary["all_available"]
        assert "text_analyzer" in all_available  # Built-in enabled
        assert "tool1" in all_available  # External
        assert "tool2" in all_available  # External
        assert "keyword_extraction" not in all_available  # Built-in disabled

    def test_remove_agent_tools(self):
        """Test removing all tools from an agent."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2"])
        tool_manager.tool_registry = mock_registry

        # Assign tools
        tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])
        assert mock_registry.access_manager.get_agent_tools("agent1")

        # Remove tools
        result = tool_manager.remove_agent_tools("agent1")
        assert result is True
        assert not mock_registry.access_manager.get_agent_tools("agent1")

        # Remove from non-existent agent
        result = tool_manager.remove_agent_tools("nonexistent_agent")
        assert result is False

    def test_get_all_agent_tools(self):
        """Test getting all agent tool assignments."""
        tool_manager = AgentToolManager(self.manifest)

        # Mock tool registry with a real assignment store
        mock_registry = make_registry(["tool1", "tool2", "tool3"])
        tool_manager.tool_registry = mock_registry

        # Assign tools to multiple agents
        tool_manager.assign_tools_to_agent("agent1", ["tool1", "tool2"])
        tool_manager.assign_tools_to_agent("agent2", ["tool2", "tool3"])

        # Get all assignments
        all_assignments = tool_manager.get_all_agent_tools()

        assert "agent1" in all_assignments
        assert "agent2" in all_assignments
        assert set(all_assignments["agent1"]) == {"tool1", "tool2"}
        assert set(all_assignments["agent2"]) == {"tool2", "tool3"}
