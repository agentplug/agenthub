"""Unit tests for tool decorator functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenthub.core.tools.decorator import tool
from agenthub.core.tools.exceptions import ToolNameConflictError, ToolValidationError
from agenthub.core.tools.registry import ToolRegistry


class TestToolDecorator:
    """Test cases for @tool decorator functionality."""

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

    @patch("mcp.client.sse.sse_client")
    @patch("mcp.ClientSession")
    def test_tool_decorator_basic_functionality(
        self, mock_session_class, mock_sse_client
    ):
        """Test basic @tool decorator functionality."""
        # Mock MCP discovery to return empty list
        mock_streams = (MagicMock(), MagicMock())
        mock_sse_client.return_value.__aenter__.return_value = mock_streams

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[]))
        mock_session_class.return_value.__aenter__.return_value = mock_session

        @tool(name="test_tool", description="A test tool")
        def test_function(param1: str, param2: int = 10) -> str:
            """Test function docstring."""
            return f"result: {param1}, {param2}"

        # Check that the function is unchanged
        assert test_function("hello", 5) == "result: hello, 5"
        assert test_function("world") == "result: world, 10"

        # Check that tool is registered
        assert "test_tool" in self.registry.get_available_tools()

        # Check tool metadata
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert metadata.function == test_function
        assert metadata.namespace == "custom"

    def test_tool_decorator_without_description(self):
        """Test @tool decorator without description parameter."""

        @tool(name="no_desc_tool")
        def no_desc_function(param: str) -> str:
            return f"no description: {param}"

        assert "no_desc_tool" in self.registry.get_available_tools()

        metadata = self.registry.get_tool_metadata("no_desc_tool")
        assert metadata.name == "no_desc_tool"
        assert metadata.description == ""

    def test_tool_decorator_name_conflict(self):
        """Test that duplicate tool names raise ToolNameConflictError."""

        @tool(name="conflict_tool", description="First tool")
        def first_tool(param: str) -> str:
            return f"first: {param}"

        with pytest.raises(ToolNameConflictError):

            @tool(name="conflict_tool", description="Second tool")
            def second_tool(param: str) -> str:
                return f"second: {param}"

    def test_tool_decorator_invalid_name(self):
        """Test that invalid tool names raise ToolValidationError."""
        with pytest.raises(ToolValidationError):

            @tool(name="", description="Empty name")
            def empty_name_tool(param: str) -> str:
                return f"empty: {param}"

    def test_tool_decorator_reserved_name(self):
        """Test that reserved names are currently allowed."""
        reserved_names = ["list", "help", "exit", "quit", "run", "execute"]

        for reserved_name in reserved_names:
            # Currently reserved names are allowed since validation is not implemented
            @tool(name=reserved_name, description="Reserved name")
            def reserved_tool(param: str) -> str:
                return f"reserved: {param}"

            # Verify the tool was registered successfully
            assert reserved_name in self.registry.get_available_tools()

    def test_tool_decorator_parameter_extraction(self):
        """Test that tool parameters are correctly extracted."""

        @tool(name="param_tool", description="Tool with parameters")
        def param_tool(
            required: str, optional: int = 42, keyword_only: str = "default"
        ) -> dict:
            """Tool with various parameter types."""
            return {
                "required": required,
                "optional": optional,
                "keyword_only": keyword_only,
            }

        metadata = self.registry.get_tool_metadata("param_tool")

        # Check parameters
        assert "required" in metadata.parameters
        assert "optional" in metadata.parameters
        assert "keyword_only" in metadata.parameters

        # Check parameter details
        required_param = metadata.parameters["required"]
        assert required_param["name"] == "required"
        assert required_param["required"] is True
        assert required_param["default"] is None

        optional_param = metadata.parameters["optional"]
        assert optional_param["name"] == "optional"
        assert optional_param["required"] is False
        assert optional_param["default"] == 42

    def test_tool_decorator_return_type_extraction(self):
        """Test that return types are correctly extracted."""

        @tool(name="return_tool", description="Tool with return type")
        def return_tool(param: str) -> dict:
            return {"result": f"success: {param}"}

        metadata = self.registry.get_tool_metadata("return_tool")
        assert metadata.return_type == "dict"

    def test_tool_decorator_examples_generation(self):
        """Test that usage examples are generated correctly."""

        @tool(name="example_tool", description="Tool for examples")
        def example_tool(param1: str, param2: int = 10) -> str:
            return f"{param1}: {param2}"

        metadata = self.registry.get_tool_metadata("example_tool")
        assert len(metadata.examples) > 0
        assert any("example_tool" in example for example in metadata.examples)

    def test_tool_decorator_thread_safety(self):
        """Test that tool registration is thread-safe."""
        import threading

        results = []
        errors = []

        def register_tool(tool_id: int):
            try:

                @tool(name=f"thread_tool_{tool_id}", description=f"Tool {tool_id}")
                def thread_tool(param: str) -> str:
                    return f"tool_{tool_id}: {param}"

                results.append(tool_id)
            except Exception as e:
                errors.append(e)

        # Create multiple threads registering tools simultaneously
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all tools were registered successfully
        assert len(errors) == 0, f"Errors during concurrent registration: {errors}"
        assert len(results) == 10

        # Check that all tools are available
        available_tools = self.registry.get_available_tools()
        for i in range(10):
            assert f"thread_tool_{i}" in available_tools

    def test_tool_decorator_with_async_function(self):
        """Test @tool decorator with async functions."""

        @tool(name="async_tool", description="Async tool")
        async def async_tool(param: str) -> str:
            await asyncio.sleep(0.01)  # Simulate async work
            return f"async_result: {param}"

        assert "async_tool" in self.registry.get_available_tools()

        metadata = self.registry.get_tool_metadata("async_tool")
        assert metadata.name == "async_tool"
        assert metadata.function == async_tool

    def test_tool_decorator_with_class_method(self):
        """Test @tool decorator with class methods."""

        class TestClass:
            @tool(name="class_method_tool", description="Class method tool")
            def class_method(self, param: str) -> str:
                return f"class_method: {param}"

        # Check tool registration
        assert "class_method_tool" in self.registry.get_available_tools()

        metadata = self.registry.get_tool_metadata("class_method_tool")
        assert metadata.name == "class_method_tool"

    def test_tool_decorator_with_static_method(self):
        """Test @tool decorator with static methods."""

        class TestClass:
            @staticmethod
            @tool(name="static_method_tool", description="Static method tool")
            def static_method(param: str) -> str:
                return f"static_method: {param}"

        assert "static_method_tool" in self.registry.get_available_tools()

        metadata = self.registry.get_tool_metadata("static_method_tool")
        assert metadata.name == "static_method_tool"

    def test_tool_decorator_preserves_function_attributes(self):
        """Test that @tool decorator preserves original function attributes."""

        def original_function(param: str) -> str:
            """Original docstring."""
            return f"original: {param}"

        original_function.custom_attr = "custom_value"
        original_function.__module__ = "test_module"

        decorated_function = tool(
            name="preserve_attr_tool", description="Preserve attributes"
        )(original_function)

        # Check that attributes are preserved
        assert decorated_function.custom_attr == "custom_value"
        assert decorated_function.__module__ == "test_module"
        assert decorated_function.__doc__ == "Original docstring."

    def test_tool_decorator_error_handling(self):
        """Test error handling in tool decorator."""
        # Test with None function
        with pytest.raises(ToolValidationError):
            tool(name="none_tool", description="None function")(None)

        # Test with non-callable
        with pytest.raises(ToolValidationError):
            tool(name="non_callable_tool", description="Non-callable")(42)

    def test_tool_decorator_metadata_completeness(self):
        """Test that tool metadata is complete and accurate."""

        @tool(name="complete_tool", description="Complete tool metadata test")
        def complete_tool(param1: str, param2: int = 10, param3: bool = True) -> dict:
            """Complete tool with all parameter types."""
            return {"param1": param1, "param2": param2, "param3": param3}

        metadata = self.registry.get_tool_metadata("complete_tool")

        # Check all required fields
        assert metadata.name == "complete_tool"
        assert metadata.description == "Complete tool metadata test"
        assert metadata.function == complete_tool
        assert metadata.namespace == "custom"
        assert metadata.return_type == "dict"

        # Check parameters
        assert len(metadata.parameters) == 3
        assert "param1" in metadata.parameters
        assert "param2" in metadata.parameters
        assert "param3" in metadata.parameters

        # Check examples
        assert len(metadata.examples) > 0
        assert all("complete_tool" in example for example in metadata.examples)
