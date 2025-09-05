"""Unit tests for the @tool decorator."""

import pytest
from agentmanager.core.tools.decorator import tool, ToolMetadata, is_tool, get_tool_metadata


class TestToolDecorator:
    """Test the @tool decorator functionality."""
    
    def test_tool_decorator_basic(self):
        """Test basic @tool decorator functionality."""
        @tool()
        def simple_tool():
            """A simple tool."""
            return "test"
        
        assert is_tool(simple_tool)
        metadata = get_tool_metadata(simple_tool)
        assert metadata is not None
        assert metadata.name == "simple_tool"
        assert metadata.description == "A simple tool."
        assert metadata.function == simple_tool
    
    def test_tool_decorator_with_name(self):
        """Test @tool decorator with custom name."""
        @tool(name="custom_name")
        def my_tool():
            """My custom tool."""
            return "test"
        
        metadata = get_tool_metadata(my_tool)
        assert metadata.name == "custom_name"
        assert metadata.description == "My custom tool."
    
    def test_tool_decorator_with_description(self):
        """Test @tool decorator with custom description."""
        @tool(description="Custom description")
        def my_tool():
            """Original docstring."""
            return "test"
        
        metadata = get_tool_metadata(my_tool)
        assert metadata.name == "my_tool"
        assert metadata.description == "Custom description"
    
    def test_tool_decorator_with_parameters(self):
        """Test @tool decorator with function parameters."""
        @tool()
        def calculator(a: int, b: int, operation: str = "add") -> str:
            """Calculate two numbers."""
            return f"{a} {operation} {b}"
        
        metadata = get_tool_metadata(calculator)
        assert metadata.name == "calculator"
        assert metadata.description == "Calculate two numbers."
        
        # Check parameters
        assert "a" in metadata.parameters
        assert "b" in metadata.parameters
        assert "operation" in metadata.parameters
        
        assert metadata.parameters["a"]["type"] == "integer"
        assert metadata.parameters["b"]["type"] == "integer"
        assert metadata.parameters["operation"]["type"] == "string"
        
        assert metadata.parameters["a"]["required"] is True
        assert metadata.parameters["b"]["required"] is True
        assert metadata.parameters["operation"]["required"] is False
        assert metadata.parameters["operation"]["default"] == "add"
    
    def test_tool_decorator_input_schema(self):
        """Test @tool decorator generates correct input schema."""
        @tool()
        def test_tool(param1: str, param2: int = 10) -> str:
            """Test tool with parameters."""
            return f"{param1}: {param2}"
        
        metadata = get_tool_metadata(test_tool)
        schema = metadata.input_schema
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        assert "param1" in schema["properties"]
        assert "param2" in schema["properties"]
        assert schema["properties"]["param1"]["type"] == "string"
        assert schema["properties"]["param2"]["type"] == "integer"
        
        assert "param1" in schema["required"]
        assert "param2" not in schema["required"]
    
    def test_tool_decorator_custom_input_schema(self):
        """Test @tool decorator with custom input schema."""
        custom_schema = {
            "type": "object",
            "properties": {
                "custom_param": {"type": "string", "description": "Custom parameter"}
            },
            "required": ["custom_param"]
        }
        
        @tool(input_schema=custom_schema)
        def custom_tool(custom_param: str) -> str:
            """Custom tool with custom schema."""
            return custom_param
        
        metadata = get_tool_metadata(custom_tool)
        assert metadata.input_schema == custom_schema
    
    def test_tool_decorator_no_docstring(self):
        """Test @tool decorator with function that has no docstring."""
        @tool()
        def no_docstring_tool():
            return "test"
        
        metadata = get_tool_metadata(no_docstring_tool)
        assert metadata.description == "Tool: no_docstring_tool"
    
    def test_tool_decorator_execution(self):
        """Test that decorated function still executes correctly."""
        @tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        # Function should still work normally
        result = add_numbers(5, 3)
        assert result == 8
        
        # Metadata should still be attached
        assert is_tool(add_numbers)
        metadata = get_tool_metadata(add_numbers)
        assert metadata.name == "add_numbers"
    
    def test_tool_decorator_multiple_decorations(self):
        """Test that multiple @tool decorations work correctly."""
        @tool(name="first_tool")
        def first_tool():
            """First tool."""
            return "first"
        
        @tool(name="second_tool")
        def second_tool():
            """Second tool."""
            return "second"
        
        assert is_tool(first_tool)
        assert is_tool(second_tool)
        
        first_metadata = get_tool_metadata(first_tool)
        second_metadata = get_tool_metadata(second_tool)
        
        assert first_metadata.name == "first_tool"
        assert second_metadata.name == "second_tool"
        assert first_metadata.function == first_tool
        assert second_metadata.function == second_tool
    
    def test_tool_metadata_class(self):
        """Test ToolMetadata class."""
        def test_func():
            return "test"
        
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            function=test_func,
            parameters={"param1": {"type": "string", "required": True}},
            input_schema={"type": "object", "properties": {}}
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.function == test_func
        assert metadata.parameters == {"param1": {"type": "string", "required": True}}
        assert metadata.input_schema == {"type": "object", "properties": {}}
    
    def test_tool_metadata_defaults(self):
        """Test ToolMetadata with default values."""
        def test_func():
            return "test"
        
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool",
            function=test_func
        )
        
        assert metadata.parameters == {}
        assert metadata.input_schema == {"type": "object", "properties": {}}
