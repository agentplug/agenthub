"""Unit tests for enhanced load_agent functionality with Phase 3 features."""

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
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

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

        # Load agent with external tools
        result = load_agent("test_agent", external_tools=["tool1", "tool2"])

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

        # Verify external tools were assigned
        mock_agent_instance.add_external_tools.assert_called_once_with(
            ["tool1", "tool2"]
        )
        mock_agent_instance.disable_builtin_tools.assert_not_called()
        mock_agent_instance.inject_knowledge.assert_not_called()

        # Should return the agent instance
        assert result == mock_agent_instance

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
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

        # Verify built-in tools were disabled
        mock_agent_instance.disable_builtin_tools.assert_called_once_with(
            ["text_analyzer"]
        )
        mock_agent_instance.add_external_tools.assert_not_called()
        mock_agent_instance.inject_knowledge.assert_not_called()

        # Should return the agent instance
        assert result == mock_agent_instance

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_with_knowledge(self, mock_create_agent, mock_load_from_yaml):
        """Test agent loading with knowledge injection (Phase 3)."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance

        # Load agent with knowledge
        knowledge_text = "You are a helpful AI assistant."
        result = load_agent("test_agent", knowledge=knowledge_text)

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

        # Verify knowledge was injected
        mock_agent_instance.inject_knowledge.assert_called_once_with(knowledge_text)
        mock_agent_instance.add_external_tools.assert_not_called()
        mock_agent_instance.disable_builtin_tools.assert_not_called()

        # Should return the agent instance
        assert result == mock_agent_instance

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

        # Load agent with external_tools parameter
        load_agent("test_agent", external_tools=["tool1", "tool2"])

        # Verify calls
        mock_load_from_yaml.assert_called_once_with("test_agent")
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

        # Verify external tools were added (backward compatibility)
        mock_agent_instance.add_external_tools.assert_called_once_with(
            ["tool1", "tool2"]
        )

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_agent_loader_error(
        self, mock_create_agent, mock_load_from_yaml
    ):
        """Test agent loading when AgentLoader raises an error."""
        # Setup mocks
        mock_load_from_yaml.side_effect = AgentLoadError("Agent not found")

        # Should raise AgentLoadError
        with pytest.raises(AgentLoadError, match="Agent not found"):
            load_agent("nonexistent_agent")

    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    @patch("agenthub.sdk.load_agent._create_agent_instance")
    def test_load_agent_both_tools_and_external_tools(
        self, mock_create_agent, mock_load_from_yaml
    ):
        """Test that specifying both 'tools' and 'external_tools' raises error."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info

        # Should raise ValidationError
        with pytest.raises(ValidationError, match="Cannot specify both"):
            load_agent("test_agent", tools=["tool1"], external_tools=["tool2"])

    @patch("agenthub.sdk.load_agent._create_agent_instance")
    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    def test_load_agent_return_value(self, mock_load_from_yaml, mock_create_agent):
        """Test that load_agent returns the agent wrapper."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_wrapper_instance = MagicMock()
        mock_create_agent.return_value = mock_wrapper_instance

        # Load agent
        agent = load_agent("test_agent")

        # Should return the wrapper instance
        assert agent == mock_wrapper_instance

    @patch("agenthub.sdk.load_agent._create_agent_instance")
    @patch("agenthub.sdk.load_agent._load_agent_from_yaml")
    def test_load_agent_tool_registry_passed_to_wrapper(
        self, mock_load_from_yaml, mock_create_agent
    ):
        """Test that tool registry is passed to AgentWrapper."""
        # Setup mocks
        mock_load_from_yaml.return_value = self.mock_agent_info
        mock_wrapper_instance = MagicMock()
        mock_create_agent.return_value = mock_wrapper_instance

        # Load agent with tools
        load_agent("test_agent", external_tools=["tool1"])

        # Verify _create_agent_instance was called
        mock_create_agent.assert_called_once_with(
            self.mock_agent_info, monitoring=False
        )

        # Verify external tools were assigned
        mock_wrapper_instance.add_external_tools.assert_called_once_with(["tool1"])
