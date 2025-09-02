"""Unit tests for tool decorators module."""

import pytest
from typing import Optional
from unittest.mock import patch, MagicMock

from agentmanager.core.tools import (
    tool, register_tool, ToolMetadata, ToolRegistry,
    get_global_registry, get_tool_metadata, is_tool, _extract_function_metadata
)


class TestToolMetadata:
    """Test ToolMetadata dataclass."""
    
    def test_tool_metadata_creation(self):
        """Test creating ToolMetadata instance."""
        def sample_func(x: int) -> str:
            return str(x)
        
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool",
            function=sample_func,
            parameters={"x": {"annotation": "int"}},
            return_type=str,
            tags=["test"]
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool"
        assert metadata.function == sample_func
        assert metadata.return_type == str
        assert metadata.tags == ["test"]
    
    def test_to_dict(self):
        """Test ToolMetadata to_dict conversion."""
        def sample_func():
            pass
        
        metadata = ToolMetadata(
            name="test",
            description="desc",
            function=sample_func,
            parameters={},
            return_type=None
        )
        
        result = metadata.to_dict()
        assert result["name"] == "test"
        assert result["description"] == "desc"
        assert result["return_type"] is None
        assert "created_at" in result


class TestToolRegistry:
    """Test ToolRegistry functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = ToolRegistry()
        self.registry.clear()
    
    def test_register_tool(self):
        """Test registering a tool."""
        def sample_func():
            pass
        
        metadata = ToolMetadata(
            name="test_tool",
            description="Test",
            function=sample_func,
            parameters={},
            return_type=None
        )
        
        self.registry.register(metadata)
        
        assert "test_tool" in self.registry.list_tools()
        assert self.registry.get_tool("test_tool") == metadata
        assert self.registry.get_function("test_tool") == sample_func
    
    def test_duplicate_registration_error(self):
        """Test error on duplicate tool registration."""
        def sample_func():
            pass
        
        metadata = ToolMetadata(
            name="duplicate",
            description="Test",
            function=sample_func,
            parameters={},
            return_type=None
        )
        
        self.registry.register(metadata)
        
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(metadata)
    
    def test_get_nonexistent_tool(self):
        """Test getting non-existent tool returns None."""
        assert self.registry.get_tool("nonexistent") is None
        assert self.registry.get_function("nonexistent") is None
    
    def test_clear_registry(self):
        """Test clearing registry."""
        def sample_func():
            pass
        
        metadata = ToolMetadata(
            name="test",
            description="Test",
            function=sample_func,
            parameters={},
            return_type=None
        )
        
        self.registry.register(metadata)
        assert len(self.registry.list_tools()) == 1
        
        self.registry.clear()
        assert len(self.registry.list_tools()) == 0


class TestFunctionMetadataExtraction:
    """Test function metadata extraction."""
    
    def test_extract_simple_function_metadata(self):
        """Test extracting metadata from simple function."""
        def simple_func(param1: str, param2: int = 42) -> bool:
            return True
        
        metadata = _extract_function_metadata(simple_func)
        
        assert "param1" in metadata
        assert "param2" in metadata
        assert metadata["param1"]["annotation"] == "<class 'str'>"
        assert metadata["param2"]["annotation"] == "<class 'int'>"
        assert metadata["param2"]["default"] == 42
    
    def test_extract_function_without_annotations(self):
        """Test extracting metadata from function without annotations."""
        def no_annotations_func(param1, param2=None):
            pass
        
        metadata = _extract_function_metadata(no_annotations_func)
        
        assert "param1" in metadata
        assert "param2" in metadata
        assert metadata["param1"]["annotation"] is None
        assert metadata["param2"]["default"] is None


class TestToolDecorator:
    """Test @tool decorator functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registry().clear()
    
    def test_tool_decorator_basic(self):
        """Test basic @tool decorator usage."""
        @tool(name="test_func", description="Test function")
        def test_function(x: int) -> str:
            return str(x)
        
        assert is_tool(test_function)
        metadata = get_tool_metadata(test_function)
        assert metadata is not None
        assert metadata.name == "test_func"
        assert metadata.description == "Test function"
    
    def test_tool_decorator_auto_name(self):
        """Test @tool decorator with automatic name detection."""
        @tool(description="Auto name test")
        def auto_name_function():
            pass
        
        metadata = get_tool_metadata(auto_name_function)
        assert metadata.name == "auto_name_function"
    
    def test_tool_decorator_with_docstring(self):
        """Test @tool decorator using function docstring."""
        @tool()
        def documented_function():
            """This is a documented function."""
            pass
        
        metadata = get_tool_metadata(documented_function)
        assert metadata.description == "This is a documented function."
    
    def test_tool_decorator_with_tags(self):
        """Test @tool decorator with tags."""
        @tool(tags=["utility", "math"])
        def tagged_function():
            pass
        
        metadata = get_tool_metadata(tagged_function)
        assert metadata.tags == ["utility", "math"]
    
    def test_tool_decorator_no_auto_register(self):
        """Test @tool decorator with auto_register=False."""
        @tool(auto_register=False)
        def not_auto_registered():
            pass
        
        # Should not be in global registry
        registry = get_global_registry()
        assert "not_auto_registered" not in registry.list_tools()
        
        # But should have metadata
        assert is_tool(not_auto_registered)
    
    def test_register_tool_decorator(self):
        """Test @register_tool convenience decorator."""
        @register_tool
        def convenience_function():
            """Convenience test."""
            pass
        
        assert is_tool(convenience_function)
        metadata = get_tool_metadata(convenience_function)
        assert metadata.name == "convenience_function"
        assert metadata.description == "Convenience test."
    
    def test_async_function_detection(self):
        """Test async function detection."""
        @tool()
        async def async_function():
            pass
        
        metadata = get_tool_metadata(async_function)
        assert metadata.is_async is True
    
    def test_sync_function_detection(self):
        """Test sync function detection."""
        @tool()
        def sync_function():
            pass
        
        metadata = get_tool_metadata(sync_function)
        assert metadata.is_async is False


class TestGlobalRegistry:
    """Test global registry functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registry().clear()
    
    def test_global_registry_singleton(self):
        """Test that global registry is singleton."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        assert registry1 is registry2
    
    def test_tool_auto_registration(self):
        """Test automatic tool registration."""
        @tool()
        def auto_registered_tool():
            pass
        
        registry = get_global_registry()
        assert "auto_registered_tool" in registry.list_tools()
    
    def test_multiple_tools_registration(self):
        """Test multiple tools registration."""
        @tool()
        def tool_one():
            pass
        
        @tool()
        def tool_two():
            pass
        
        registry = get_global_registry()
        tools = registry.list_tools()
        assert "tool_one" in tools
        assert "tool_two" in tools
        assert len(tools) == 2


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_is_tool_with_decorated_function(self):
        """Test is_tool with decorated function."""
        @tool()
        def decorated_func():
            pass
        
        assert is_tool(decorated_func) is True
    
    def test_is_tool_with_regular_function(self):
        """Test is_tool with regular function."""
        def regular_func():
            pass
        
        assert is_tool(regular_func) is False
    
    def test_get_tool_metadata_with_metadata(self):
        """Test get_tool_metadata with decorated function."""
        @tool(name="test")
        def func_with_metadata():
            pass
        
        metadata = get_tool_metadata(func_with_metadata)
        assert metadata is not None
        assert metadata.name == "test"
    
    def test_get_tool_metadata_without_metadata(self):
        """Test get_tool_metadata with regular function."""
        def func_without_metadata():
            pass
        
        metadata = get_tool_metadata(func_without_metadata)
        assert metadata is None
