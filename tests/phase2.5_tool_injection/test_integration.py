"""Integration tests for Phase 2.5 tool injection functionality."""

import unittest.mock
from unittest.mock import MagicMock, patch

import pytest

from agenthub.core.tools.decorator import tool
from agenthub.core.tools.exceptions import ToolNameConflictError, ToolNotFoundError
from agenthub.core.tools.registry import ToolRegistry
from agenthub.sdk.load_agent import load_agent


class TestToolInjectionIntegration:
    """Integration tests for the complete tool injection workflow."""

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

        # Also patch the decorator's registry reference
        self.decorator_patcher = patch(
            "agenthub.core.tools.decorator._registry", self.registry
        )
        self.decorator_patcher.start()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "registry_patcher"):
            self.registry_patcher.stop()
        if hasattr(self, "decorator_patcher"):
            self.decorator_patcher.stop()

    def test_complete_tool_injection_workflow(self):
        """Test the complete tool injection workflow from registration to execution."""

        # Step 1: Register tools using @tool decorator
        @tool(name="calculator", description="Basic calculator operations")
        def calculator(operation: str, a: float, b: float) -> float:
            """Perform basic arithmetic operations."""
            if operation == "add":
                return a + b
            elif operation == "subtract":
                return a - b
            elif operation == "multiply":
                return a * b
            elif operation == "divide":
                return b != 0 and a / b or 0
            else:
                raise ValueError(f"Unknown operation: {operation}")

        @tool(name="text_processor", description="Process text data")
        def text_processor(text: str, operation: str = "uppercase") -> str:
            """Process text with various operations."""
            if operation == "uppercase":
                return text.upper()
            elif operation == "lowercase":
                return text.lower()
            elif operation == "reverse":
                return text[::-1]
            else:
                return text

        # Step 2: Verify tools are registered
        available_tools = self.registry.get_available_tools()
        assert "calculator" in available_tools
        assert "text_processor" in available_tools

        # Step 3: Get tool metadata
        calc_metadata = self.registry.get_tool_metadata("calculator")
        assert calc_metadata.name == "calculator"
        assert calc_metadata.description == "Basic calculator operations"
        assert "operation" in calc_metadata.parameters
        assert "a" in calc_metadata.parameters
        assert "b" in calc_metadata.parameters

        text_metadata = self.registry.get_tool_metadata("text_processor")
        assert text_metadata.name == "text_processor"
        assert text_metadata.description == "Process text data"

        # Step 4: Assign tools to agent
        self.registry.assign_tools_to_agent(
            "test_agent", ["calculator", "text_processor"]
        )
        agent_tools = self.registry.get_agent_tools("test_agent")
        assert set(agent_tools) == {"calculator", "text_processor"}

        # Step 5: Execute tools
        calc_result = self.registry.execute_tool(
            "calculator", {"operation": "add", "a": 5, "b": 3}
        )
        assert calc_result == 8

        text_result = self.registry.execute_tool(
            "text_processor", {"text": "Hello World", "operation": "uppercase"}
        )
        assert text_result == "HELLO WORLD"

    def test_tool_context_generation(self):
        """Test tool context generation for agents."""

        # Register tools
        @tool(name="data_analyzer", description="Analyze data patterns")
        def data_analyzer(data: list, analysis_type: str = "basic") -> dict:
            """Analyze data and return insights."""
            return {
                "type": analysis_type,
                "count": len(data),
                "insights": f"Analyzed {len(data)} items",
            }

        @tool(name="file_processor", description="Process files")
        def file_processor(file_path: str, operation: str) -> str:
            """Process files with various operations."""
            return f"Processed {file_path} with {operation}"

        # Assign tools to agent
        self.registry.assign_tools_to_agent(
            "analysis_agent", ["data_analyzer", "file_processor"]
        )

        # Get tool context
        agent_tools = self.registry.get_agent_tools("analysis_agent")
        tool_context = {
            "available_tools": agent_tools,
            "tool_descriptions": {},
            "tool_usage_examples": {},
            "tool_parameters": {},
            "tool_return_types": {},
            "tool_namespaces": {},
        }

        # Populate tool context
        for tool_name in agent_tools:
            metadata = self.registry.get_tool_metadata(tool_name)
            tool_context["tool_descriptions"][tool_name] = metadata.description
            tool_context["tool_usage_examples"][tool_name] = metadata.examples
            tool_context["tool_parameters"][tool_name] = metadata.parameters
            tool_context["tool_return_types"][tool_name] = metadata.return_type
            tool_context["tool_namespaces"][tool_name] = metadata.namespace

        # Verify tool context
        assert "data_analyzer" in tool_context["available_tools"]
        assert "file_processor" in tool_context["available_tools"]
        assert (
            "Analyze data patterns"
            in tool_context["tool_descriptions"]["data_analyzer"]
        )
        assert "Process files" in tool_context["tool_descriptions"]["file_processor"]

    @patch("agenthub.sdk.load_agent.AgentLoader")
    @patch("agenthub.sdk.load_agent.AgentWrapper")
    def test_agent_loading_with_tools(self, mock_wrapper_class, mock_loader_class):
        """Test loading an agent with tool assignments."""

        # Register tools
        @tool(name="web_search", description="Search the web")
        def web_search(query: str, max_results: int = 10) -> list:
            """Search the web for information."""
            return [f"Result {i+1} for '{query}'" for i in range(min(max_results, 3))]

        @tool(name="data_processor", description="Process data")
        def data_processor(data: str, format: str = "json") -> dict:
            """Process data in various formats."""
            return {"data": data, "format": format, "processed": True}

        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_agent.return_value = {
            "name": "research_agent",
            "path": "/path/to/agent",
            "valid": True,
            "manifest": {
                "name": "research_agent",
                "description": "Research agent",
                "version": "1.0.0",
                "entry_point": "agent.py",
                "methods": ["research", "analyze", "summarize"],
            },
        }
        mock_loader_class.return_value = mock_loader_instance

        mock_wrapper_instance = MagicMock()
        mock_wrapper_class.return_value = mock_wrapper_instance

        # Mock tool registry
        mock_tool_registry = MagicMock()
        mock_tool_registry.get_available_tools.return_value = [
            "web_search",
            "data_processor",
            "other_tool",
        ]

        with patch(
            "agenthub.sdk.load_agent.get_tool_registry",
            return_value=mock_tool_registry,
        ):
            # Load agent with tools
            load_agent("research_agent", tools=["web_search", "data_processor"])

            # Verify calls
            mock_loader_instance.load_agent.assert_called_once_with(
                "default", "research_agent"
            )
            mock_wrapper_class.assert_called_once_with(
                mock_loader_instance.load_agent.return_value,
                tool_registry=unittest.mock.ANY,
                agent_id="default/research_agent",
                assigned_tools=["web_search", "data_processor"],
                runtime=unittest.mock.ANY,
            )
            mock_wrapper_instance.assign_tools.assert_not_called()

    def test_concurrent_tool_registration(self):
        """Test concurrent tool registration and execution."""
        import threading
        import time

        results = []
        errors = []

        def register_and_execute_tool(tool_id: int):
            try:

                @tool(
                    name=f"concurrent_tool_{tool_id}",
                    description=f"Concurrent tool {tool_id}",
                )
                def concurrent_tool(value: int) -> int:
                    time.sleep(0.01)  # Simulate work
                    return value * 2

                # Execute the tool
                result = self.registry.execute_tool(
                    f"concurrent_tool_{tool_id}", {"value": tool_id}
                )
                results.append((tool_id, result))
            except Exception as e:
                errors.append((tool_id, e))

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_and_execute_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors during concurrent execution: {errors}"
        assert len(results) == 10

        # Verify all tools are registered
        available_tools = self.registry.get_available_tools()
        for i in range(10):
            assert f"concurrent_tool_{i}" in available_tools

        # Verify execution results
        for tool_id, result in results:
            assert result == tool_id * 2

    def test_tool_metadata_completeness(self):
        """Test that tool metadata is complete and accurate."""

        @tool(
            name="metadata_test_tool",
            description="Tool for testing metadata completeness",
        )
        def metadata_test_tool(
            required_param: str, optional_param: int = 42, keyword_only: str = "default"
        ) -> dict:
            """Tool with various parameter types for metadata testing."""
            return {
                "required": required_param,
                "optional": optional_param,
                "keyword": keyword_only,
            }

        # Get metadata
        metadata = self.registry.get_tool_metadata("metadata_test_tool")

        # Verify basic fields
        assert metadata.name == "metadata_test_tool"
        assert metadata.description == "Tool for testing metadata completeness"
        assert metadata.function == metadata_test_tool
        assert metadata.namespace == "custom"
        assert metadata.return_type == "dict"

        # Verify parameters
        assert len(metadata.parameters) == 3
        assert "required_param" in metadata.parameters
        assert "optional_param" in metadata.parameters
        assert "keyword_only" in metadata.parameters

        # Verify parameter details
        required = metadata.parameters["required_param"]
        assert required["name"] == "required_param"
        assert required["type"] is str
        assert required["required"] is True
        assert required["default"] is None

        optional = metadata.parameters["optional_param"]
        assert optional["name"] == "optional_param"
        assert optional["type"] is int
        assert optional["required"] is False
        assert optional["default"] == 42

        keyword = metadata.parameters["keyword_only"]
        assert keyword["name"] == "keyword_only"
        assert keyword["type"] is str
        assert keyword["required"] is False
        assert keyword["default"] == "default"

        # Verify examples
        assert len(metadata.examples) > 0
        assert all("metadata_test_tool" in example for example in metadata.examples)

    def test_error_handling_throughout_workflow(self):
        """Test error handling throughout the tool injection workflow."""

        # Test 1: Duplicate tool registration
        @tool(name="duplicate_tool", description="First tool")
        def first_tool():
            return "first"

        with pytest.raises(ToolNameConflictError):  # Should raise ToolNameConflictError

            @tool(name="duplicate_tool", description="Second tool")
            def second_tool():
                return "second"

        # Test 2: Tool execution with invalid parameters
        @tool(name="error_test_tool", description="Tool for error testing")
        def error_test_tool(param: str) -> str:
            return f"result: {param}"

        # Should raise TypeError for missing required parameter
        with pytest.raises(TypeError):
            self.registry.execute_tool("error_test_tool", {})

        # Test 3: Tool execution with non-existent tool
        with pytest.raises(ToolNotFoundError):  # Should raise ToolNotFoundError
            self.registry.execute_tool("nonexistent_tool", {"param": "value"})

        # Test 4: Agent tool assignment with non-existent tools
        with pytest.raises(ToolNotFoundError):  # Should raise ToolNotFoundError
            self.registry.assign_tools_to_agent("test_agent", ["nonexistent_tool"])

    def test_tool_registry_statistics(self):
        """Test tool registry statistics functionality."""

        # Register some tools
        @tool(name="stat_tool1", description="Statistics tool 1")
        def stat_tool1():
            return "tool1"

        @tool(name="stat_tool2", description="Statistics tool 2")
        def stat_tool2():
            return "tool2"

        # Assign tools to agents
        self.registry.assign_tools_to_agent("agent1", ["stat_tool1"])
        self.registry.assign_tools_to_agent("agent2", ["stat_tool1", "stat_tool2"])

        # Get statistics
        stats = self.registry.get_statistics()

        # Verify statistics
        assert stats["total_tools"] == 2
        assert stats["total_agents"] == 2
        assert stats["tools_per_agent"]["agent1"] == 1
        assert stats["tools_per_agent"]["agent2"] == 2

    def test_tool_registry_cleanup(self):
        """Test tool registry cleanup functionality."""

        # Register tools and assign to agents
        @tool(name="cleanup_tool", description="Tool for cleanup testing")
        def cleanup_tool():
            return "cleanup"

        self.registry.assign_tools_to_agent("cleanup_agent", ["cleanup_tool"])

        # Verify tools and assignments exist
        assert "cleanup_tool" in self.registry.get_available_tools()
        assert len(self.registry.get_agent_tools("cleanup_agent")) == 1

        # Cleanup
        self.registry.cleanup()

        # Verify everything is cleared (except built-in tools from MCP discovery)
        available_tools = self.registry.get_available_tools()
        assert "cleanup_tool" not in available_tools  # Our test tool should be gone
        assert len(self.registry.agent_tool_access) == 0
