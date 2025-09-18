"""Unit tests for enhanced load_agent functionality with Phase 3 features."""

import unittest.mock
from unittest.mock import MagicMock, patch

import pytest

from agenthub.core.tools.exceptions import AgentLoadError, ValidationError
from agenthub.sdk.load_agent import load_agent


class TestLoadAgent:
    """Test cases for enhanced load_agent functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Mock the agent loader
        self.mock_agent_loader = MagicMock()
        self.mock_agent_wrapper = MagicMock()

        # Mock agent info with Phase 3 features
        self.mock_agent_info = {
            "name": "test_agent",
            "namespace": "default",
            "path": "/path/to/agent",
            "valid": True,
            "manifest": {
                "name": "test_agent",
                "description": "Test agent",
                "version": "1.0.0",
                "entry_point": "agent.py",
                "methods": ["run", "analyze", "process"],
                "builtin_tools": {
                    "text_analyzer": {
                        "description": "Analyze text content",
                        "required": True,
                        "parameters": {"text": {"type": "string", "required": True}},
                    }
                },
            },
        }

        self.mock_agent_loader.load_agent.return_value = self.mock_agent_info
        self.mock_agent_wrapper.return_value = self.mock_agent_wrapper

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_basic(self, mock_create_agent, mock_load_from_yaml):
        """Test basic agent loading without tools."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent
        result = load_agent("test_agent")

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(self.mock_agent_info)

        # Should return the agent instance
        assert result == mock_agent_instance

        # Verify no tools were assigned
        mock_agent_instance.add_external_tools.assert_not_called()
        mock_agent_instance.disable_builtin_tools.assert_not_called()
        mock_agent_instance.inject_knowledge.assert_not_called()

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_with_external_tools(
        self, mock_create_agent, mock_load_from_yaml
    ):
        """Test agent loading with external tools (Phase 3)."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent with external tools (Phase 3)
        result = load_agent("test_agent", external_tools=["tool1", "tool2"])

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(self.mock_agent_info)

        # Should return the agent instance
        assert result == mock_agent_instance

        # Verify external tools were added
        mock_agent_instance.add_external_tools.assert_called_once_with(
            ["tool1", "tool2"]
        )

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_with_builtin_tools_disabled(
        self, mock_create_agent, mock_load_from_yaml
    ):
        """Test agent loading with disabled built-in tools (Phase 3)."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent with disabled built-in tools
        result = load_agent("test_agent", disabled_builtin_tools=["text_analyzer"])

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(self.mock_agent_info)

        # Should return the agent instance
        assert result == mock_agent_instance

        # Verify built-in tools were disabled
        mock_agent_instance.disable_builtin_tools.assert_called_once_with(
            ["text_analyzer"]
        )

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_with_knowledge(self, mock_create_agent, mock_load_from_yaml):
        """Test agent loading with knowledge injection (Phase 3)."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent with knowledge
        result = load_agent("test_agent", knowledge="You are a helpful AI assistant.")

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(self.mock_agent_info)

        # Should return the agent instance
        assert result == mock_agent_instance

        # Verify knowledge was injected
        mock_agent_instance.inject_knowledge.assert_called_once_with(
            "You are a helpful AI assistant."
        )

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_backward_compatibility(
        self, mock_create_agent, mock_load_from_yaml
    ):
        """Test backward compatibility with deprecated 'tools' parameter."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent with deprecated 'tools' parameter
        with pytest.warns(DeprecationWarning, match="'tools' parameter is deprecated"):
            result = load_agent("test_agent", tools=["tool1", "tool2"])

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(self.mock_agent_info)

        # Should return the agent instance
        assert result == mock_agent_instance

        # Verify external tools were added (backward compatibility)
        mock_agent_instance.add_external_tools.assert_called_once_with(
            ["tool1", "tool2"]
        )

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_load_agent_namespace_format(self, mock_wrapper_class, mock_loader_class):
        """Test agent loading with namespace/agent_name format."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Load agent with namespace
        load_agent("namespace/agent_name")

        # Verify calls
        mock_loader_instance.load_agent.assert_called_once_with(
            "namespace", "agent_name"
        )
        mock_wrapper_class.assert_called_once_with(
            self.mock_agent_info,
            tool_registry=unittest.mock.ANY,
            agent_id="namespace/agent_name",
            assigned_tools=[],
            runtime=unittest.mock.ANY,
        )

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    @patch("agenthub.core.tools.registry._registry")
    def test_load_agent_tool_not_found(
        self, mock_registry, mock_wrapper_class, mock_loader_class
    ):
        """Test agent loading with non-existent tools raises error."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry with limited tools
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = ["tool1", "tool2"]
        mock_registry.get_available_tools.return_value = ["tool1", "tool2"]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Should raise error for non-existent tool
            with pytest.raises(ValueError, match="Tools not found"):
                load_agent("test_agent", tools=["nonexistent_tool"])

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_load_agent_empty_tools_list(self, mock_wrapper_class, mock_loader_class):
        """Test agent loading with empty tools list."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Load agent with empty tools list
        load_agent("test_agent", tools=[])

        # Verify calls
        mock_loader_instance.load_agent.assert_called_once_with("default", "test_agent")
        mock_wrapper_class.assert_called_once_with(
            self.mock_agent_info,
            tool_registry=unittest.mock.ANY,
            agent_id="default/test_agent",
            assigned_tools=[],
            runtime=unittest.mock.ANY,
        )

        # Should not assign tools
        mock_wrapper_instance.assign_tools.assert_not_called()

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_load_agent_no_tool_registry(self, mock_wrapper_class, mock_loader_class):
        """Test agent loading when no tool registry is available."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock no tool registry available
        with patch("agenthub.sdk.load_agent.get_tool_registry", return_value=None):
            # Should work without tools
            load_agent("test_agent")

            # Verify calls
            mock_loader_instance.load_agent.assert_called_once_with(
                "default", "test_agent"
            )
            mock_wrapper_class.assert_called_once_with(
                self.mock_agent_info,
                tool_registry=None,
                agent_id="default/test_agent",
                assigned_tools=[],
                runtime=unittest.mock.ANY,
            )

            # Should not assign tools
            mock_wrapper_instance.assign_tools.assert_not_called()

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    @patch("agenthub.core.tools.registry._registry")
    def test_load_agent_tool_validation(
        self, mock_registry, mock_wrapper_class, mock_loader_class
    ):
        """Test tool validation during agent loading."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = [
            "tool1",
            "tool2",
            "tool3",
        ]
        mock_registry.get_available_tools.return_value = [
            "tool1",
            "tool2",
            "tool3",
        ]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Load agent with valid tools
            load_agent("test_agent", tools=["tool1", "tool2"])

            # Verify tool validation was called
            mock_tool_registry.get_available_tools.assert_called_once()
            # assign_tools is not called since tools are passed directly to constructor
            mock_wrapper_instance.assign_tools.assert_not_called()

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_load_agent_agent_loader_error(self, mock_wrapper_class, mock_loader_class):
        """Test agent loading when AgentLoader raises an error."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.side_effect = Exception("Agent not found")
        mock_loader_class.return_value = mock_loader_instance

        # Should raise the error
        with pytest.raises(Exception, match="Agent not found"):
            load_agent("nonexistent_agent")

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    @patch("agenthub.core.tools.registry._registry")
    def test_load_agent_tool_assignment_error(
        self, mock_registry, mock_wrapper_class, mock_loader_class
    ):
        """Test agent loading when tool assignment raises an error."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry with limited tools
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = ["tool1", "tool2"]
        mock_registry.get_available_tools.return_value = ["tool1", "tool2"]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Should raise error for non-existent tool
            with pytest.raises(ValueError, match="Tools not found"):
                load_agent("test_agent", tools=["nonexistent_tool"])

    def test_load_agent_invalid_agent_name(self):
        """Test load_agent with invalid agent name."""
        with pytest.raises(AgentLoadError):
            load_agent("")

    def test_load_agent_invalid_tools_type(self):
        """Test load_agent with invalid tools type."""
        with pytest.raises(ValidationError):
            load_agent("test_agent", external_tools="not_a_list")

    def test_load_agent_both_tools_and_external_tools(self):
        """Test load_agent with both deprecated tools and external_tools parameters."""
        with pytest.raises(
            ValidationError, match="Cannot specify both 'tools' and 'external_tools'"
        ):
            load_agent("test_agent", tools=["tool1"], external_tools=["tool2"])

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    @patch("agenthub.core.tools.registry._registry")
    def test_load_agent_with_mcp_tools(
        self, mock_registry, mock_wrapper_class, mock_loader_class
    ):
        """Test agent loading with MCP-discovered tools."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry with MCP tools
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = [
            "local_tool",
            "mcp_tool1",
            "mcp_tool2",
        ]
        mock_registry.get_available_tools.return_value = [
            "local_tool",
            "mcp_tool1",
            "mcp_tool2",
        ]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Load agent with MCP tools
            load_agent("test_agent", tools=["local_tool", "mcp_tool1"])

            # Verify calls
            mock_loader_instance.load_agent.assert_called_once_with(
                "default", "test_agent"
            )
            mock_wrapper_class.assert_called_once_with(
                self.mock_agent_info,
                tool_registry=unittest.mock.ANY,
                agent_id="default/test_agent",
                assigned_tools=["local_tool", "mcp_tool1"],
                runtime=unittest.mock.ANY,
            )
            mock_wrapper_instance.assign_tools.assert_not_called()

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_load_agent_return_value(self, mock_wrapper_class, mock_loader_class):
        """Test that load_agent returns the agent wrapper."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Load agent
        agent = load_agent("test_agent")

        # Should return the wrapper instance
        assert agent == mock_wrapper_instance

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    @patch("agenthub.core.tools.registry._registry")
    def test_load_agent_tool_registry_passed_to_wrapper(
        self, mock_registry, mock_wrapper_class, mock_loader_class
    ):
        """Test that tool registry is passed to AgentWrapper."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = self.mock_agent_info
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = ["tool1", "tool2"]
        mock_registry.get_available_tools.return_value = ["tool1", "tool2"]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Load agent with tools
            load_agent("test_agent", tools=["tool1"])

            # Verify tool registry was passed to wrapper
            mock_wrapper_class.assert_called_once_with(
                self.mock_agent_info,
                tool_registry=unittest.mock.ANY,
                agent_id="default/test_agent",
                assigned_tools=["tool1"],
                runtime=unittest.mock.ANY,
            )
