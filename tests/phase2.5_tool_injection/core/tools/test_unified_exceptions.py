"""Unit tests for unified exception system."""

from agenthub.core.tools.exceptions import (
    AgentExecutionError,
    AgentHubError,
    AgentLoadError,
    ConfigurationError,
    InstallationError,
    KnowledgeError,
    ToolAccessDeniedError,
    ToolConflictError,
    ToolError,
    ToolNotFoundError,
    ValidationError,
)


class TestUnifiedExceptions:
    """Test cases for unified exception system."""

    def test_agent_hub_error_base(self):
        """Test base AgentHubError functionality."""
        # Test basic error
        error = AgentHubError("Test error")
        assert str(error) == "Test error"
        assert error.suggestions == []
        assert error.context == {}

        # Test error with suggestions
        error = AgentHubError("Test error", ["Suggestion 1", "Suggestion 2"])
        assert "Test error" in str(error)
        assert "Suggestion 1" in str(error)
        assert "Suggestion 2" in str(error)
        assert error.suggestions == ["Suggestion 1", "Suggestion 2"]

        # Test error with context
        error = AgentHubError("Test error", context={"key": "value"})
        assert error.context == {"key": "value"}

    def test_agent_load_error(self):
        """Test AgentLoadError functionality."""
        error = AgentLoadError("Failed to load", "test-agent", ["Check agent name"])
        assert error.agent_name == "test-agent"
        assert error.suggestions == ["Check agent name"]
        assert "Failed to load" in str(error)
        assert "test-agent" in str(error)

    def test_agent_execution_error(self):
        """Test AgentExecutionError functionality."""
        error = AgentExecutionError(
            "Execution failed", "run_method", {"param": "value"}
        )
        assert error.method_name == "run_method"
        assert error.parameters == {"param": "value"}
        assert "Execution failed" in str(error)

    def test_validation_error(self):
        """Test ValidationError functionality."""
        error = ValidationError("Invalid parameter", "param1", "string", 123)
        assert error.parameter_name == "param1"
        assert error.expected_type == "string"
        assert error.actual_value == 123

        # Test custom string representation
        error_str = str(error)
        assert "Validation failed for parameter 'param1'" in error_str
        assert "expected string" in error_str
        assert "got int" in error_str

    def test_installation_error(self):
        """Test InstallationError functionality."""
        error = InstallationError("Command failed", "pip install", 1)
        assert error.command == "pip install"
        assert error.exit_code == 1

        # Test custom string representation
        error_str = str(error)
        assert "Installation failed for command 'pip install'" in error_str
        assert "Command failed" in error_str

    def test_knowledge_error(self):
        """Test KnowledgeError functionality."""
        error = KnowledgeError("Knowledge operation failed", "inject")
        assert error.operation == "inject"
        assert "Knowledge operation failed" in str(error)

    def test_configuration_error(self):
        """Test ConfigurationError functionality."""
        error = ConfigurationError("Invalid config", "config.yaml", "api_key")
        assert error.config_file == "config.yaml"
        assert error.field == "api_key"
        assert "Invalid config" in str(error)

    def test_tool_conflict_error(self):
        """Test ToolConflictError functionality."""
        error = ToolConflictError(
            "Tool conflict", tool_name="test_tool", conflict_type="builtin_conflict"
        )
        assert error.tool_name == "test_tool"
        assert error.conflict_type == "builtin_conflict"
        assert "Tool conflict" in str(error)

    def test_tool_error_hierarchy(self):
        """Test tool error inheritance hierarchy."""
        # ToolError should inherit from AgentHubError
        tool_error = ToolError("Tool error")
        assert isinstance(tool_error, AgentHubError)

        # ToolNotFoundError should inherit from ToolError
        not_found_error = ToolNotFoundError("Tool not found")
        assert isinstance(not_found_error, ToolError)
        assert isinstance(not_found_error, AgentHubError)

        # ToolAccessDeniedError should inherit from ToolError
        access_error = ToolAccessDeniedError("Access denied")
        assert isinstance(access_error, ToolError)
        assert isinstance(access_error, AgentHubError)

    def test_exception_suggestions_formatting(self):
        """Test that suggestions are properly formatted in error messages."""
        error = AgentHubError(
            "Something went wrong",
            [
                "Try checking your configuration",
                "Verify the agent exists",
                "Check the logs",
            ],
        )

        error_str = str(error)
        assert "Something went wrong" in error_str
        assert "Suggestions:" in error_str
        assert "• Try checking your configuration" in error_str
        assert "• Verify the agent exists" in error_str
        assert "• Check the logs" in error_str

    def test_exception_without_suggestions(self):
        """Test that exceptions without suggestions don't show suggestions section."""
        error = AgentHubError("Simple error")
        error_str = str(error)
        assert error_str == "Simple error"
        assert "Suggestions:" not in error_str

    def test_validation_error_without_parameter_info(self):
        """Test ValidationError without parameter information."""
        error = ValidationError("General validation failed")
        error_str = str(error)
        assert error_str == "General validation failed"
        assert "Validation failed for parameter" not in error_str

    def test_installation_error_without_command(self):
        """Test InstallationError without command information."""
        error = InstallationError("General installation failed")
        error_str = str(error)
        assert error_str == "General installation failed"
        assert "Installation failed for command" not in error_str

    def test_exception_context_preservation(self):
        """Test that exception context is preserved."""
        context = {
            "agent_id": "test/agent",
            "timestamp": "2025-01-27T10:00:00Z",
            "operation": "load",
        }
        error = AgentHubError("Error occurred", context=context)
        assert error.context == context

    def test_exception_inheritance_chain(self):
        """Test the complete inheritance chain for all exceptions."""
        # All exceptions should inherit from AgentHubError
        exceptions = [
            AgentLoadError("test"),
            AgentExecutionError("test"),
            ValidationError("test"),
            ToolConflictError("test"),
            InstallationError("test"),
            KnowledgeError("test"),
            ConfigurationError("test"),
            ToolError("test"),
            ToolNotFoundError("test"),
            ToolAccessDeniedError("test"),
        ]

        for exc in exceptions:
            assert isinstance(
                exc, AgentHubError
            ), f"{type(exc).__name__} should inherit from AgentHubError"
            assert isinstance(
                exc, Exception
            ), f"{type(exc).__name__} should inherit from Exception"
