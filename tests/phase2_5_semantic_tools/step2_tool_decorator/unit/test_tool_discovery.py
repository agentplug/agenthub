"""Unit tests for tool discovery system."""

import pytest
from agentmanager.core.tools.decorator import tool
from agentmanager.core.tools.discovery import ToolDiscovery


class TestToolDiscovery:
    """Test the tool discovery functionality."""
    
    def test_discovery_initialization(self):
        """Test ToolDiscovery initialization."""
        discovery = ToolDiscovery()
        assert discovery.discovered_tools == {}
        assert discovery._discovery_cache == set()
    
    def test_discover_tools_basic(self):
        """Test discovering tools from a list of functions."""
        @tool(name="tool1")
        def tool1():
            """First tool."""
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            """Second tool."""
            return "tool2"
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([tool1, tool2])
        
        assert len(discovered) == 2
        assert len(discovery.discovered_tools) == 2
        
        tool_names = [tool.name for tool in discovered]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
    
    def test_discover_tools_auto_register(self):
        """Test auto-registration of undecorated functions."""
        def undecorated_tool():
            """Undecorated tool."""
            return "undecorated"
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([undecorated_tool])
        
        assert len(discovered) == 1
        assert len(discovery.discovered_tools) == 1
        
        tool_metadata = discovered[0]
        assert tool_metadata.name == "undecorated_tool"
        assert tool_metadata.description == "Undecorated tool."
    
    def test_discover_tools_mixed(self):
        """Test discovering mix of decorated and undecorated functions."""
        @tool(name="decorated_tool")
        def decorated_tool():
            """Decorated tool."""
            return "decorated"
        
        def undecorated_tool():
            """Undecorated tool."""
            return "undecorated"
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([decorated_tool, undecorated_tool])
        
        assert len(discovered) == 2
        assert len(discovery.discovered_tools) == 2
        
        tool_names = [tool.name for tool in discovered]
        assert "decorated_tool" in tool_names
        assert "undecorated_tool" in tool_names
    
    def test_get_tool(self):
        """Test getting a specific tool by name."""
        @tool(name="test_tool")
        def test_tool():
            """Test tool."""
            return "test"
        
        discovery = ToolDiscovery()
        discovery.discover_tools([test_tool])
        
        # Get existing tool
        tool_metadata = discovery.get_tool("test_tool")
        assert tool_metadata is not None
        assert tool_metadata.name == "test_tool"
        
        # Get non-existing tool
        non_existing = discovery.get_tool("non_existing")
        assert non_existing is None
    
    def test_list_tools(self):
        """Test listing all discovered tools."""
        @tool(name="tool1")
        def tool1():
            return "tool1"
        
        @tool(name="tool2")
        def tool2():
            return "tool2"
        
        discovery = ToolDiscovery()
        discovery.discover_tools([tool1, tool2])
        
        tools = discovery.list_tools()
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
        
        discovery = ToolDiscovery()
        discovery.discover_tools([tool1, tool2])
        
        names = discovery.get_tool_names()
        assert len(names) == 2
        assert "tool1" in names
        assert "tool2" in names
    
    def test_clear_tools(self):
        """Test clearing all discovered tools."""
        @tool(name="test_tool")
        def test_tool():
            return "test"
        
        discovery = ToolDiscovery()
        discovery.discover_tools([test_tool])
        
        assert len(discovery.discovered_tools) == 1
        
        discovery.clear_tools()
        
        assert len(discovery.discovered_tools) == 0
        assert len(discovery._discovery_cache) == 0
    
    def test_discover_tools_from_module(self):
        """Test discovering tools from a module."""
        # Create a mock module with tools
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
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools_from_module(mock_module)
        
        assert len(discovered) == 2
        tool_names = [tool.name for tool in discovered]
        assert "module_tool1" in tool_names
        assert "module_tool2" in tool_names
    
    def test_discover_tools_from_object(self):
        """Test discovering tools from an object."""
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
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools_from_object(mock_object)
        
        assert len(discovered) == 2
        tool_names = [tool.name for tool in discovered]
        assert "object_tool1" in tool_names
        assert "object_tool2" in tool_names
    
    def test_parameter_extraction(self):
        """Test parameter extraction from function signatures."""
        @tool()
        def test_tool(param1: str, param2: int = 10, param3: bool = True) -> str:
            """Test tool with parameters."""
            return f"{param1}: {param2}: {param3}"
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([test_tool])
        
        assert len(discovered) == 1
        tool_metadata = discovered[0]
        
        parameters = tool_metadata.parameters
        assert "param1" in parameters
        assert "param2" in parameters
        assert "param3" in parameters
        
        assert parameters["param1"]["type"] == "string"
        assert parameters["param1"]["required"] is True
        
        assert parameters["param2"]["type"] == "integer"
        assert parameters["param2"]["required"] is False
        assert parameters["param2"]["default"] == 10
        
        assert parameters["param3"]["type"] == "boolean"
        assert parameters["param3"]["required"] is False
        assert parameters["param3"]["default"] is True
    
    def test_input_schema_generation(self):
        """Test input schema generation."""
        @tool()
        def test_tool(param1: str, param2: int = 10) -> str:
            """Test tool."""
            return f"{param1}: {param2}"
        
        discovery = ToolDiscovery()
        discovered = discovery.discover_tools([test_tool])
        
        assert len(discovered) == 1
        tool_metadata = discovered[0]
        
        schema = tool_metadata.input_schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        assert "param1" in schema["properties"]
        assert "param2" in schema["properties"]
        assert schema["properties"]["param1"]["type"] == "string"
        assert schema["properties"]["param2"]["type"] == "integer"
        
        assert "param1" in schema["required"]
        assert "param2" not in schema["required"]
