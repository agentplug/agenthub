"""Integration tests for Step 2: @tool decorator and tool discovery."""

import pytest
from agentmanager.core.tools import tool, ToolDiscovery, ToolRegistry
from agentmanager.core.mcp import MCPServer


class TestStep2Integration:
    """Integration tests for Step 2 functionality."""
    
    def test_complete_step2_workflow(self):
        """Test the complete Step 2 workflow: decorator -> discovery -> registry -> MCP."""
        
        # Step 1: Define tools with @tool decorator
        @tool(name="integration_calculator", description="Calculator for integration testing")
        def calculator(a: int, b: int, operation: str = "add") -> str:
            """Calculate two numbers with specified operation."""
            if operation == "add":
                return f"{a} + {b} = {a + b}"
            elif operation == "multiply":
                return f"{a} × {b} = {a * b}"
            else:
                return f"Unknown operation: {operation}"
        
        @tool(name="integration_text_processor", description="Text processor for integration testing")
        def text_processor(text: str, action: str = "uppercase") -> str:
            """Process text with specified action."""
            if action == "uppercase":
                return text.upper()
            elif action == "lowercase":
                return text.lower()
            else:
                return f"Unknown action: {action}"
        
        # Step 2: Discover tools
        discovery = ToolDiscovery()
        tool_functions = [calculator, text_processor]
        discovered_tools = discovery.discover_tools(tool_functions)
        
        assert len(discovered_tools) == 2
        tool_names = [tool.name for tool in discovered_tools]
        assert "integration_calculator" in tool_names
        assert "integration_text_processor" in tool_names
        
        # Step 3: Register tools with registry
        registry = ToolRegistry()
        registered_count = registry.register_tool_functions(tool_functions)
        
        assert registered_count == 2
        assert registry.get_tool_count() == 2
        assert "integration_calculator" in registry.get_tool_names()
        assert "integration_text_processor" in registry.get_tool_names()
        
        # Step 4: Test tool execution through registry
        result = registry.execute_tool("integration_calculator", a=10, b=5, operation="add")
        assert result == "10 + 5 = 15"
        
        result = registry.execute_tool("integration_text_processor", text="hello", action="uppercase")
        assert result == "HELLO"
        
        # Step 5: Test MCP integration
        mcp_server = MCPServer(name="Integration Test Server", version="1.0.0")
        
        for tool_metadata in discovered_tools:
            mcp_server.register_tool(
                tool_metadata.name,
                tool_metadata.description,
                tool_metadata.function
            )
        
        assert mcp_server.get_tool_count() == 2
        assert "integration_calculator" in mcp_server.tools
        assert "integration_text_processor" in mcp_server.tools
        
        # Step 6: Test tool schemas
        schemas = registry.get_tool_schemas()
        assert len(schemas) == 2
        assert "integration_calculator" in schemas
        assert "integration_text_processor" in schemas
        
        # Verify schema structure
        calc_schema = schemas["integration_calculator"]
        assert calc_schema["name"] == "integration_calculator"
        assert calc_schema["description"] == "Calculator for integration testing"
        assert "inputSchema" in calc_schema
        assert calc_schema["inputSchema"]["type"] == "object"
        assert "properties" in calc_schema["inputSchema"]
        assert "required" in calc_schema["inputSchema"]
    
    def test_auto_registration_workflow(self):
        """Test auto-registration of undecorated functions."""
        
        # Define undecorated function
        def undecorated_tool(param: str) -> str:
            """Undecorated tool for testing."""
            return f"Processed: {param}"
        
        # Discover and auto-register
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([undecorated_tool])
        
        assert len(discovered) == 1
        tool_metadata = discovered[0]
        assert tool_metadata.name == "undecorated_tool"
        assert tool_metadata.description == "Undecorated tool for testing."
        
        # Register with registry
        registry = ToolRegistry()
        count = registry.register_tool_functions([undecorated_tool])
        
        assert count == 1
        assert registry.get_tool_count() == 1
        
        # Test execution
        result = registry.execute_tool("undecorated_tool", param="test")
        assert result == "Processed: test"
    
    def test_mixed_tool_types_workflow(self):
        """Test workflow with mix of decorated and undecorated tools."""
        
        @tool(name="decorated_tool")
        def decorated_tool(value: int) -> int:
            """Decorated tool."""
            return value * 2
        
        def undecorated_tool(value: int) -> int:
            """Undecorated tool."""
            return value + 1
        
        # Discover both types
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([decorated_tool, undecorated_tool])
        
        assert len(discovered) == 2
        tool_names = [tool.name for tool in discovered]
        assert "decorated_tool" in tool_names
        assert "undecorated_tool" in tool_names
        
        # Register both
        registry = ToolRegistry()
        count = registry.register_tool_functions([decorated_tool, undecorated_tool])
        
        assert count == 2
        assert registry.get_tool_count() == 2
        
        # Test both tools
        result1 = registry.execute_tool("decorated_tool", value=5)
        assert result1 == 10
        
        result2 = registry.execute_tool("undecorated_tool", value=5)
        assert result2 == 6
    
    def test_parameter_validation_workflow(self):
        """Test parameter validation in the complete workflow."""
        
        @tool(name="validation_tool")
        def validation_tool(required_param: str, optional_param: int = 10) -> str:
            """Tool for testing parameter validation."""
            return f"{required_param}: {optional_param}"
        
        registry = ToolRegistry()
        registry.register_tool_functions([validation_tool])
        
        # Test valid parameters
        valid = registry.validate_tool_parameters("validation_tool", required_param="test", optional_param=20)
        assert valid is True
        
        # Test missing required parameter
        valid = registry.validate_tool_parameters("validation_tool", optional_param=20)
        assert valid is False
        
        # Test valid with default
        valid = registry.validate_tool_parameters("validation_tool", required_param="test")
        assert valid is True
        
        # Test execution with valid parameters
        result = registry.execute_tool("validation_tool", required_param="test", optional_param=20)
        assert result == "test: 20"
        
        result = registry.execute_tool("validation_tool", required_param="test")
        assert result == "test: 10"
    
    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow."""
        
        @tool(name="error_tool")
        def error_tool(should_error: bool = False) -> str:
            """Tool that can raise errors."""
            if should_error:
                raise ValueError("Test error")
            return "success"
        
        registry = ToolRegistry()
        registry.register_tool_functions([error_tool])
        
        # Test successful execution
        result = registry.execute_tool("error_tool", should_error=False)
        assert result == "success"
        
        # Test error execution
        with pytest.raises(ValueError, match="Test error"):
            registry.execute_tool("error_tool", should_error=True)
        
        # Test non-existent tool
        with pytest.raises(KeyError, match="Tool 'non_existent' not found"):
            registry.execute_tool("non_existent", param="value")
    
    def test_tool_metadata_preservation(self):
        """Test that tool metadata is preserved throughout the workflow."""
        
        @tool(name="metadata_tool", description="Tool for testing metadata preservation")
        def metadata_tool(param1: str, param2: int = 5) -> str:
            """Tool with specific metadata."""
            return f"{param1}: {param2}"
        
        # Test discovery preserves metadata
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([metadata_tool])
        
        assert len(discovered) == 1
        tool_metadata = discovered[0]
        assert tool_metadata.name == "metadata_tool"
        assert tool_metadata.description == "Tool for testing metadata preservation"
        assert tool_metadata.function == metadata_tool
        
        # Test parameters are preserved
        assert "param1" in tool_metadata.parameters
        assert "param2" in tool_metadata.parameters
        assert tool_metadata.parameters["param1"]["type"] == "string"
        assert tool_metadata.parameters["param2"]["type"] == "integer"
        assert tool_metadata.parameters["param1"]["required"] is True
        assert tool_metadata.parameters["param2"]["required"] is False
        assert tool_metadata.parameters["param2"]["default"] == 5
        
        # Test input schema is preserved
        schema = tool_metadata.input_schema
        assert schema["type"] == "object"
        assert "param1" in schema["properties"]
        assert "param2" in schema["properties"]
        assert "param1" in schema["required"]
        assert "param2" not in schema["required"]
        
        # Test registry preserves metadata
        registry = ToolRegistry()
        registry.register_tool_functions([metadata_tool])
        
        registered_tool = registry.get_tool("metadata_tool")
        assert registered_tool is not None
        assert registered_tool.name == "metadata_tool"
        assert registered_tool.description == "Tool for testing metadata preservation"
        assert registered_tool.function == metadata_tool
