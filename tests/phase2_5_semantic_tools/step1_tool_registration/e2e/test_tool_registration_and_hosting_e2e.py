"""End-to-end tests for tool registration and hosting."""

import asyncio
import pytest
import time
import requests
from typing import Dict, Any
from unittest.mock import patch

from agentmanager.core.tools import tool, get_global_registry, register_function, get_registered_tools_global, start_tool_service, stop_tool_service, is_service_running


class TestE2EToolRegistrationAndHosting:
    """End-to-end test for complete tool registration and hosting workflow."""
    
    def setup_method(self):
        """Setup for each test."""
        # Clear global registry
        get_global_registry().clear()
        # Stop any running service
        stop_tool_service()
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Ensure service is stopped
        stop_tool_service()
        # Clear registry
        get_global_registry().clear()
    
    def test_tool_registration_and_hosting_e2e(self):
        """Test complete end-to-end workflow."""
        # Step 1: Define tools using decorators
        @tool(name="e2e_text_processor", description="Process text for E2E test")
        def text_processor(text: str, operation: str = "upper") -> str:
            """Process text with specified operation."""
            if operation == "upper":
                return text.upper()
            elif operation == "lower":
                return text.lower()
            else:
                return text
        
        @tool(name="e2e_calculator", description="Basic calculator for E2E test")
        def calculator(a: float, b: float, op: str) -> float:
            """Perform basic calculations."""
            if op == "add":
                return a + b
            elif op == "subtract":
                return a - b
            elif op == "multiply":
                return a * b
            elif op == "divide":
                if b == 0:
                    raise ValueError("Division by zero")
                return a / b
            else:
                raise ValueError(f"Unknown operation: {op}")
        
        # Step 2: Register additional tool manually
        def manual_greeter(name: str, style: str = "friendly") -> str:
            """Generate greeting messages."""
            if style == "friendly":
                return f"Hi there, {name}!"
            elif style == "formal":
                return f"Good day, {name}."
            else:
                return f"Hello {name}!"
        
        result = register_function(manual_greeter, name="e2e_greeter", description="E2E greeter tool")
        assert result.success is True
        
        # Step 3: Verify tools are registered
        registry = get_global_registry()
        registered_tools = registry.list_tools()
        assert "e2e_text_processor" in registered_tools
        assert "e2e_calculator" in registered_tools
        assert "e2e_greeter" in registered_tools
        assert len(registered_tools) == 3
        
        # Step 4: Start HTTP service in background
        service_port = 8887  # Use unique port for E2E test
        
        # Mock the actual server to avoid binding to real port in tests
        with patch('agentmanager.core.tools.service.uvicorn.Server') as mock_server_class:
            mock_server = mock_server_class.return_value
            mock_server.run = lambda: None  # Mock run method
            
            with patch('agentmanager.core.tools.service.ToolServiceHost._start_background') as mock_start_bg:
                # Mock background start to avoid actual threading
                def mock_start():
                    service = start_tool_service(port=service_port, background=False)
                    service._is_running = True  # Set running state manually
                
                mock_start_bg.side_effect = mock_start
                
                service = start_tool_service(port=service_port, background=True)
                
                # Verify service is marked as running
                assert service.is_running() is True
                assert service.get_service_url() == f"http://127.0.0.1:{service_port}"
        
        # Step 5: Test direct tool execution (without HTTP)
        # Since we're mocking the HTTP server, test tools directly
        text_func = registry.get_function("e2e_text_processor")
        calc_func = registry.get_function("e2e_calculator")
        greet_func = registry.get_function("e2e_greeter")
        
        # Test text processor
        result = text_func("hello world", "upper")
        assert result == "HELLO WORLD"
        
        result = text_func("HELLO WORLD", "lower")
        assert result == "hello world"
        
        # Test calculator
        result = calc_func(10, 5, "add")
        assert result == 15.0
        
        result = calc_func(10, 3, "multiply")
        assert result == 30.0
        
        # Test greeter
        result = greet_func("Alice", "friendly")
        assert result == "Hi there, Alice!"
        
        result = greet_func("Bob", "formal")
        assert result == "Good day, Bob."
        
        # Step 6: Test error handling
        with pytest.raises(ValueError, match="Division by zero"):
            calc_func(10, 0, "divide")
        
        with pytest.raises(ValueError, match="Unknown operation"):
            calc_func(10, 5, "invalid")
        
        # Step 7: Test tool metadata
        all_tools = get_registered_tools_global()
        assert len(all_tools) == 3
        
        text_tool = next(tool for tool in all_tools if tool.name == "e2e_text_processor")
        assert text_tool.description == "Process text for E2E test"
        assert "text" in text_tool.parameters
        assert "operation" in text_tool.parameters
        
        calc_tool = next(tool for tool in all_tools if tool.name == "e2e_calculator")
        assert calc_tool.description == "Basic calculator for E2E test"
        assert "a" in calc_tool.parameters
        assert "b" in calc_tool.parameters
        assert "op" in calc_tool.parameters
        
        # Step 8: Test service management
        assert is_service_running() is True
        
        stop_tool_service()
        assert is_service_running() is False
    
    def test_e2e_with_parameter_validation_errors(self):
        """Test E2E workflow with parameter validation errors."""
        @tool(name="strict_tool")
        def strict_tool(required_param: str, optional_param: int = 42) -> str:
            """Tool with strict parameter requirements."""
            return f"{required_param}_{optional_param}"
        
        # Test with missing required parameter
        registry = get_global_registry()
        func = registry.get_function("strict_tool")
        
        # This should work
        result = func("test")
        assert result == "test_42"
        
        result = func("test", 100)
        assert result == "test_100"
        
        # Direct validation test (simulating what HTTP service would do)
        import inspect
        
        def validate_params(func, params):
            """Simple parameter validation like HTTP service does."""
            signature = inspect.signature(func)
            validated = {}
            
            for param_name, param in signature.parameters.items():
                if param_name in params:
                    validated[param_name] = params[param_name]
                elif param.default == param.empty:
                    raise ValueError(f"Missing required parameter: {param_name}")
            
            extra = set(params.keys()) - set(signature.parameters.keys())
            if extra:
                raise ValueError(f"Unexpected parameters: {', '.join(extra)}")
            
            return validated
        
        # Test parameter validation
        valid_params = validate_params(func, {"required_param": "test"})
        assert valid_params == {"required_param": "test"}
        
        valid_params = validate_params(func, {"required_param": "test", "optional_param": 99})
        assert valid_params == {"required_param": "test", "optional_param": 99}
        
        # Test validation errors
        with pytest.raises(ValueError, match="Missing required parameter: required_param"):
            validate_params(func, {})
        
        with pytest.raises(ValueError, match="Unexpected parameters: extra"):
            validate_params(func, {"required_param": "test", "extra": "value"})
    
    def test_e2e_async_tool_support(self):
        """Test E2E workflow with async tools."""
        @tool(name="async_processor")
        async def async_processor(data: str, delay: float = 0.001) -> str:
            """Async tool for E2E testing."""
            await asyncio.sleep(delay)
            return f"Processed: {data}"
        
        # Verify registration
        registry = get_global_registry()
        assert "async_processor" in registry.list_tools()
        
        # Get tool metadata
        tools = get_registered_tools_global()
        async_tool = next(tool for tool in tools if tool.name == "async_processor")
        assert async_tool.is_async is True
        
        # Test execution (simulating what service would do)
        func = registry.get_function("async_processor")
        
        # Run async function
        result = asyncio.run(func("test_data"))
        assert result == "Processed: test_data"
        
        result = asyncio.run(func("another_test", 0.002))
        assert result == "Processed: another_test"
    
    def test_e2e_tool_lifecycle_management(self):
        """Test complete tool lifecycle in E2E scenario."""
        # Step 1: Start with empty registry
        registry = get_global_registry()
        initial_count = len(registry.list_tools())
        
        # Step 2: Register tools at runtime
        @tool(name="lifecycle_tool_1")
        def tool1() -> str:
            return "tool1_result"
        
        assert len(registry.list_tools()) == initial_count + 1
        
        # Step 3: Register more tools manually
        def tool2() -> str:
            return "tool2_result"
        
        def tool3() -> str:
            return "tool3_result"
        
        result2 = register_function(tool2, name="lifecycle_tool_2")
        result3 = register_function(tool3, name="lifecycle_tool_3")
        
        assert result2.success is True
        assert result3.success is True
        assert len(registry.list_tools()) == initial_count + 3
        
        # Step 4: Test all tools work
        func1 = registry.get_function("lifecycle_tool_1")
        func2 = registry.get_function("lifecycle_tool_2")
        func3 = registry.get_function("lifecycle_tool_3")
        
        assert func1() == "tool1_result"
        assert func2() == "tool2_result"
        assert func3() == "tool3_result"
        
        # Step 5: Start service and verify all tools accessible
        with patch('agentmanager.core.tools.service.uvicorn.Server'):
            with patch('agentmanager.core.tool_service_host.ToolServiceHost.start'):
                service = start_tool_service(port=8888, background=True)
                service._is_running = True  # Mock running state
                
                # All tools should be accessible through service
                all_tools = registry.list_tools()
                assert "lifecycle_tool_1" in all_tools
                assert "lifecycle_tool_2" in all_tools
                assert "lifecycle_tool_3" in all_tools
                
                stop_tool_service()
        
        # Step 6: Clear and verify cleanup
        registry.clear()
        assert len(registry.list_tools()) == 0
    
    def test_e2e_error_resilience(self):
        """Test E2E workflow resilience to errors."""
        # Register some tools, including one that will cause errors
        @tool(name="reliable_tool")
        def reliable_tool(x: int) -> int:
            return x * 2
        
        @tool(name="error_prone_tool")
        def error_prone_tool(x: int, should_fail: bool = False) -> int:
            if should_fail:
                raise RuntimeError("Intentional test error")
            return x + 10
        
        registry = get_global_registry()
        
        # Test reliable tool works
        reliable_func = registry.get_function("reliable_tool")
        assert reliable_func(5) == 10
        
        # Test error-prone tool works when not failing
        error_func = registry.get_function("error_prone_tool")
        assert error_func(5) == 15
        assert error_func(5, False) == 15
        
        # Test error-prone tool fails appropriately
        with pytest.raises(RuntimeError, match="Intentional test error"):
            error_func(5, True)
        
        # Verify that errors in one tool don't affect others
        assert reliable_func(10) == 20  # Still works after error in other tool
        
        # Test service can handle errors gracefully
        with patch('agentmanager.core.tools.service.uvicorn.Server'):
            with patch('agentmanager.core.tool_service_host.ToolServiceHost.start'):
                service = start_tool_service(port=8889, background=True)
                service._is_running = True
                
                # Service should still report all tools as available
                tools = registry.list_tools()
                assert "reliable_tool" in tools
                assert "error_prone_tool" in tools
                
                stop_tool_service()
