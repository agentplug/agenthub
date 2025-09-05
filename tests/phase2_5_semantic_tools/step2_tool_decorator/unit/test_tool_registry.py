"""Unit tests for tool registry."""

import pytest
from agentmanager.core.tools.decorator import tool
from agentmanager.core.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test the tool registry functionality."""
    
    def test_registry_initialization(self):
        """Test ToolRegistry initialization."""
        registry = ToolRegistry()
        assert registry.registered_tools == {}
        assert registry.discovery is not None
        assert registry._mcp_servers == {}
    
    def test_register_tool_function(self):
        """Test registering a single tool function."""
        @tool(name="test_tool")
        def test_tool():
            """Test tool."""
            return "test"
        
        registry = ToolRegistry()
        success = registry.register_tool_function(test_tool)
        
        assert success is True
        assert len(registry.registered_tools) == 1
        assert "test_tool" in registry.registered_tools
    
    def test_register_tool_functions(self):
        """Test registering multiple tool functions."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        registry = ToolRegistry()
        count = registry.register_tool_functions([tool1, tool2])
        
        assert count == 2
        assert len(registry.registered_tools) == 2
        assert "tool1" in registry.registered_tools
        assert "tool2" in registry.registered_tools
    
    def test_register_tools_from_module(self):
        """Test registering tools from a module."""
        import types
        
        mock_module = types.ModuleType("mock_module")
        
        @tool(name="module_tool1")
        def tool1():
            return "tool1"
        
        @tool(name="module_tool2")
        def tool2():
            return "tool2"
        
        def not_a_tool():
            return "not_a_tool"
        
        # Add functions to module
        mock_module.tool1 = tool1
        mock_module.tool2 = tool2
        mock_module.not_a_tool = not_a_tool
        
        registry = ToolRegistry()
        count = registry.register_tools_from_module(mock_module)
        
        assert count == 2
        assert len(registry.registered_tools) == 2
        assert "module_tool1" in registry.registered_tools
        assert "module_tool2" in registry.registered_tools
    
    def test_register_tools_from_object(self):
        """Test registering tools from an object."""
        class MockObject:
            @tool(name="object_tool1")
            def tool1(self):
                return "tool1"
            
            @tool(name="object_tool2")
            def tool2(self):
                return "tool2"
            
            def not_a_tool(self):
                return "not_a_tool"
        
        mock_object = MockObject()
        registry = ToolRegistry()
        count = registry.register_tools_from_object(mock_object)
        
        assert count == 2
        assert len(registry.registered_tools) == 2
        assert "object_tool1" in registry.registered_tools
        assert "object_tool2" in registry.registered_tools
    
    def test_get_tool(self):
        """Test getting a specific tool."""
        @tool(name="test_tool")
        def test_tool():
            return "test"
        
        registry = ToolRegistry()
        registry.register_tool_function(test_tool)
        
        # Get existing tool
        tool_metadata = registry.get_tool("test_tool")
        assert tool_metadata is not None
        assert tool_metadata.name == "test_tool"
        
        # Get non-existing tool
        non_existing = registry.get_tool("non_existing")
        assert non_existing is None
    
    def test_list_tools(self):
        """Test listing all registered tools."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        registry = ToolRegistry()
        registry.register_tool_functions([tool1, tool2])
        
        tools = registry.list_tools()
        assert len(tools) == 2
        
        tool_names = [tool.name for tool in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
    
    def test_get_tool_names(self):
        """Test getting list of tool names."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        registry = ToolRegistry()
        registry.register_tool_functions([tool1, tool2])
        
        names = registry.get_tool_names()
        assert len(names) == 2
        assert "tool1" in names
        assert "tool2" in names
    
    def test_get_tool_count(self):
        """Test getting the number of registered tools."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        registry = ToolRegistry()
        assert registry.get_tool_count() == 0
        
        registry.register_tool_functions([tool1, tool2])
        assert registry.get_tool_count() == 2
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        @tool(name="test_tool")
        def test_tool():
            return "test"
        
        registry = ToolRegistry()
        registry.register_tool_function(test_tool)
        
        assert len(registry.registered_tools) == 1
        
        # Unregister existing tool
        success = registry.unregister_tool("test_tool")
        assert success is True
        assert len(registry.registered_tools) == 0
        
        # Unregister non-existing tool
        success = registry.unregister_tool("non_existing")
        assert success is False
    
    def test_clear_tools(self):
        """Test clearing all registered tools."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        registry = ToolRegistry()
        registry.register_tool_functions([tool1, tool2])
        
        assert len(registry.registered_tools) == 2
        
        registry.clear_tools()
        
        assert len(registry.registered_tools) == 0
    
    def test_get_tool_schemas(self):
        """Test getting MCP-compatible schemas."""
        @tool(name="test_tool", description="Test tool description")
        def test_tool(param1: str, param2: int = 10) -> str:
            """Test tool with parameters."""
            return f"{param1}: {param2}"
        
        registry = ToolRegistry()
        registry.register_tool_function(test_tool)
        
        schemas = registry.get_tool_schemas()
        
        assert len(schemas) == 1
        assert "test_tool" in schemas
        
        schema = schemas["test_tool"]
        assert schema["name"] == "test_tool"
        assert schema["description"] == "Test tool description"
        assert "inputSchema" in schema
        assert schema["inputSchema"]["type"] == "object"
    
    def test_execute_tool(self):
        """Test executing a registered tool."""
        @tool(name="calculator")
        def calculator(a: int, b: int, operation: str = "add") -> str:
            """Simple calculator."""
            if operation == "add":
                return f"{a} + {b} = {a + b}"
            elif operation == "multiply":
                return f"{a} × {b} = {a * b}"
            else:
                return f"Unknown operation: {operation}"
        
        registry = ToolRegistry()
        registry.register_tool_function(calculator)
        
        # Test tool execution
        result = registry.execute_tool("calculator", a=10, b=5, operation="add")
        assert result == "10 + 5 = 15"
        
        result = registry.execute_tool("calculator", a=10, b=5, operation="multiply")
        assert result == "10 × 5 = 50"
        
        # Test with default parameter
        result = registry.execute_tool("calculator", a=10, b=5)
        assert result == "10 + 5 = 15"
    
    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        registry = ToolRegistry()
        
        with pytest.raises(KeyError, match="Tool 'non_existing' not found"):
            registry.execute_tool("non_existing", param="value")
    
    def test_execute_tool_error(self):
        """Test tool execution with error."""
        @tool(name="error_tool")
        def error_tool():
            """Tool that raises an error."""
            raise ValueError("Test error")
        
        registry = ToolRegistry()
        registry.register_tool_function(error_tool)
        
        with pytest.raises(ValueError, match="Test error"):
            registry.execute_tool("error_tool")
    
    def test_validate_tool_parameters(self):
        """Test parameter validation."""
        @tool(name="test_tool")
        def test_tool(param1: str, param2: int = 10) -> str:
            """Test tool with parameters."""
            return f"{param1}: {param2}"
        
        registry = ToolRegistry()
        registry.register_tool_function(test_tool)
        
        # Valid parameters
        valid = registry.validate_tool_parameters("test_tool", param1="test", param2=20)
        assert valid is True
        
        # Missing required parameter
        valid = registry.validate_tool_parameters("test_tool", param2=20)
        assert valid is False
        
        # Valid with default parameter
        valid = registry.validate_tool_parameters("test_tool", param1="test")
        assert valid is True
        
        # Non-existent tool
        valid = registry.validate_tool_parameters("non_existing", param="value")
        assert valid is False
    
    def test_validate_parameter_types(self):
        """Test parameter type validation."""
        @tool(name="type_test_tool")
        def type_test_tool(string_param: str, int_param: int, bool_param: bool) -> str:
            """Tool for testing parameter types."""
            return f"{string_param}: {int_param}: {bool_param}"
        
        registry = ToolRegistry()
        registry.register_tool_function(type_test_tool)
        
        # Valid types
        valid = registry.validate_tool_parameters(
            "type_test_tool", 
            string_param="test", 
            int_param=123, 
            bool_param=True
        )
        assert valid is True
        
        # Invalid string type
        valid = registry.validate_tool_parameters(
            "type_test_tool", 
            string_param=123,  # Should be string
            int_param=123, 
            bool_param=True
        )
        assert valid is False
        
        # Invalid int type
        valid = registry.validate_tool_parameters(
            "type_test_tool", 
            string_param="test", 
            int_param="not_an_int",  # Should be int
            bool_param=True
        )
        assert valid is False
        
        # Invalid bool type
        valid = registry.validate_tool_parameters(
            "type_test_tool", 
            string_param="test", 
            int_param=123, 
            bool_param="not_a_bool"  # Should be bool
        )
        assert valid is False
