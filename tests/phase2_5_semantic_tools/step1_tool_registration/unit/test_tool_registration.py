"""Unit tests for tool registration module."""

import pytest
from unittest.mock import Mock, patch

from agentmanager.core.tool_registration import (
    ToolRegistrationManager, ToolRegistrationResult, ToolRegistrationError,
    register_tools, register_function, get_registered_tools_global,
    is_tool_registered_global, get_tool_function_global,
    get_global_registration_manager
)
from agentmanager.core.tool_decorators import tool, ToolRegistry


class TestToolRegistrationResult:
    """Test ToolRegistrationResult dataclass."""
    
    def test_success_result(self):
        """Test successful registration result."""
        result = ToolRegistrationResult(
            success=True,
            tool_name="test_tool",
            message="Success",
            errors=[],
            warnings=[]
        )
        
        assert result.success is True
        assert result.tool_name == "test_tool"
        assert result.message == "Success"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_failure_result(self):
        """Test failed registration result."""
        result = ToolRegistrationResult(
            success=False,
            tool_name="failed_tool",
            message="Failed",
            errors=["Error 1", "Error 2"]
        )
        
        assert result.success is False
        assert len(result.errors) == 2


class TestToolRegistrationManager:
    """Test ToolRegistrationManager functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = ToolRegistry()
        self.registry.clear()
        self.manager = ToolRegistrationManager(registry=self.registry)
    
    def test_register_simple_function(self):
        """Test registering a simple function."""
        def simple_func(x: int) -> str:
            return str(x)
        
        result = self.manager.register_function(simple_func)
        
        assert result.success is True
        assert result.tool_name == "simple_func"
        assert result.metadata is not None
        assert self.manager.is_tool_registered("simple_func")
    
    def test_register_function_with_custom_name(self):
        """Test registering function with custom name."""
        def func():
            pass
        
        result = self.manager.register_function(
            func, 
            name="custom_name",
            description="Custom description"
        )
        
        assert result.success is True
        assert result.tool_name == "custom_name"
        assert result.metadata.description == "Custom description"
    
    def test_register_function_with_tags(self):
        """Test registering function with tags."""
        def tagged_func():
            pass
        
        result = self.manager.register_function(
            tagged_func,
            tags=["utility", "test"]
        )
        
        assert result.success is True
        assert result.metadata.tags == ["utility", "test"]
    
    def test_register_duplicate_function_without_force(self):
        """Test registering duplicate function without force."""
        def func():
            pass
        
        # First registration should succeed
        result1 = self.manager.register_function(func)
        assert result1.success is True
        
        # Second registration should fail
        result2 = self.manager.register_function(func)
        assert result2.success is False
        assert "already registered" in result2.message
    
    def test_register_duplicate_function_with_force(self):
        """Test registering duplicate function with force override."""
        def func():
            pass
        
        # First registration
        result1 = self.manager.register_function(func)
        assert result1.success is True
        
        # Second registration with force should succeed
        result2 = self.manager.register_function(func, force=True)
        assert result2.success is True
    
    def test_register_non_callable(self):
        """Test registering non-callable object."""
        not_callable = "not a function"
        
        result = self.manager.register_function(not_callable)
        
        assert result.success is False
        assert "not callable" in result.message
    
    def test_register_function_without_name(self):
        """Test registering function without __name__ attribute."""
        class CallableWithoutName:
            def __call__(self):
                pass
        
        callable_obj = CallableWithoutName()
        
        result = self.manager.register_function(callable_obj)
        
        assert result.success is False
        assert "does not have a name" in result.message
    
    def test_register_decorated_function(self):
        """Test registering function that's already decorated."""
        # Clear any existing tools first
        self.registry.clear()
        
        @tool(name="decorated_func", description="Already decorated", auto_register=False)
        def decorated_func():
            pass
        
        result = self.manager.register_function(decorated_func)
        
        assert result.success is True
        assert result.metadata.name == "decorated_func"
        assert result.metadata.description == "Already decorated"
    
    def test_register_multiple_functions(self):
        """Test registering multiple functions."""
        def func1():
            pass
        
        def func2():
            pass
        
        results = self.manager.register_multiple([func1, func2])
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert results[0].tool_name == "func1"
        assert results[1].tool_name == "func2"
    
    def test_get_registered_tools(self):
        """Test getting all registered tools."""
        def func1():
            pass
        
        def func2():
            pass
        
        self.manager.register_function(func1)
        self.manager.register_function(func2)
        
        tools = self.manager.get_registered_tools()
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "func1" in tool_names
        assert "func2" in tool_names
    
    def test_get_tool_function(self):
        """Test getting tool function by name."""
        def test_func():
            return "test_result"
        
        self.manager.register_function(test_func)
        
        retrieved_func = self.manager.get_tool_function("test_func")
        assert retrieved_func is test_func
        assert retrieved_func() == "test_result"
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        def func():
            pass
        
        self.manager.register_function(func)
        assert self.manager.is_tool_registered("func")
        
        success = self.manager.unregister_tool("func")
        assert success is True
        assert not self.manager.is_tool_registered("func")
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering non-existent tool."""
        success = self.manager.unregister_tool("nonexistent")
        assert success is False
    
    def test_clear_all_tools(self):
        """Test clearing all tools."""
        def func1():
            pass
        
        def func2():
            pass
        
        self.manager.register_function(func1)
        self.manager.register_function(func2)
        assert len(self.manager.get_registered_tools()) == 2
        
        self.manager.clear_all()
        assert len(self.manager.get_registered_tools()) == 0
    
    def test_validation_enable_disable(self):
        """Test enabling/disabling validation."""
        assert self.manager._enable_validation is True
        
        self.manager.enable_validation(False)
        assert self.manager._enable_validation is False
        
        self.manager.enable_validation(True)
        assert self.manager._enable_validation is True


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registration_manager().clear_all()
    
    def test_register_function_global(self):
        """Test global register_function."""
        def global_func():
            pass
        
        result = register_function(global_func)
        
        assert result.success is True
        assert is_tool_registered_global("global_func")
    
    def test_register_tools_global(self):
        """Test global register_tools."""
        def func1():
            pass
        
        def func2():
            pass
        
        results = register_tools([func1, func2])
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert is_tool_registered_global("func1")
        assert is_tool_registered_global("func2")
    
    def test_get_registered_tools_global(self):
        """Test global get_registered_tools."""
        def func():
            pass
        
        register_function(func)
        
        tools = get_registered_tools_global()
        assert len(tools) == 1
        assert tools[0].name == "func"
    
    def test_get_tool_function_global(self):
        """Test global get_tool_function."""
        def test_func():
            return "global_test"
        
        register_function(test_func)
        
        retrieved_func = get_tool_function_global("test_func")
        assert retrieved_func is test_func
        assert retrieved_func() == "global_test"
    
    def test_is_tool_registered_global(self):
        """Test global is_tool_registered."""
        def registered_func():
            pass
        
        assert not is_tool_registered_global("registered_func")
        
        register_function(registered_func)
        
        assert is_tool_registered_global("registered_func")
        assert not is_tool_registered_global("unregistered_func")


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = ToolRegistry()
        self.registry.clear()
        self.manager = ToolRegistrationManager(registry=self.registry)
    
    def test_registration_with_exception(self):
        """Test registration when exception occurs."""
        def problematic_func():
            pass
        
        # Mock registry to raise exception
        with patch.object(self.registry, 'register', side_effect=Exception("Test error")):
            result = self.manager.register_function(problematic_func)
            
            assert result.success is False
            assert "Test error" in result.message
    
    def test_function_validation_edge_cases(self):
        """Test edge cases in function validation."""
        # Test with lambda (has __name__)
        lambda_func = lambda x: x
        result = self.manager.register_function(lambda_func)
        assert result.success is True
        
        # Test with function that has no __name__ (edge case)
        class CallableWithoutName:
            def __call__(self):
                pass
        
        callable_obj = CallableWithoutName()
        result = self.manager.register_function(callable_obj)
        assert result.success is False
        assert "does not have a name" in result.message


class TestAsyncFunctionSupport:
    """Test async function registration."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = ToolRegistry()
        self.registry.clear()
        self.manager = ToolRegistrationManager(registry=self.registry)
    
    def test_register_async_function(self):
        """Test registering async function."""
        async def async_func():
            return "async_result"
        
        result = self.manager.register_function(async_func)
        
        assert result.success is True
        assert result.metadata.is_async is True
        assert result.tool_name == "async_func"
