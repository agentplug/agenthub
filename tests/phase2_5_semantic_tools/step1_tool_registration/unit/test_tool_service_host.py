"""Unit tests for tool service host module."""

import asyncio
import pytest
import threading
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from agentmanager.core.tools import (
    ToolServiceHost, ServiceConfiguration,
    ToolExecutionRequest, ToolExecutionResponse, 
    ToolInfoResponse, ToolListResponse,
    start_tool_service, stop_tool_service, get_global_service_host, is_service_running
)
from agentmanager.core.tools import tool, get_global_registry


class TestServiceConfiguration:
    """Test ServiceConfiguration dataclass."""
    
    def test_default_configuration(self):
        """Test default service configuration."""
        config = ServiceConfiguration()
        
        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.log_level == "info"
        assert config.workers == 1
        assert config.thread_pool_max_workers == 10
    
    def test_custom_configuration(self):
        """Test custom service configuration."""
        config = ServiceConfiguration(
            host="0.0.0.0",
            port=9000,
            log_level="debug",
            workers=2,
            thread_pool_max_workers=20
        )
        
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.log_level == "debug"
        assert config.workers == 2
        assert config.thread_pool_max_workers == 20


class TestRequestResponseModels:
    """Test Pydantic request/response models."""
    
    def test_tool_execution_request_default(self):
        """Test ToolExecutionRequest with defaults."""
        request = ToolExecutionRequest()
        
        assert request.parameters == {}
        assert request.execution_id is None
    
    def test_tool_execution_request_with_data(self):
        """Test ToolExecutionRequest with data."""
        request = ToolExecutionRequest(
            parameters={"param1": "value1"},
            execution_id="test-123"
        )
        
        assert request.parameters == {"param1": "value1"}
        assert request.execution_id == "test-123"
    
    def test_tool_execution_response(self):
        """Test ToolExecutionResponse."""
        response = ToolExecutionResponse(
            success=True,
            result="test_result",
            execution_time=0.5,
            execution_id="test-123"
        )
        
        assert response.success is True
        assert response.result == "test_result"
        assert response.execution_time == 0.5
        assert response.execution_id == "test-123"
        assert response.error is None
    
    def test_tool_info_response(self):
        """Test ToolInfoResponse."""
        response = ToolInfoResponse(
            name="test_tool",
            description="Test description",
            parameters={"param": {"type": "str"}},
            return_type="str",
            is_async=False,
            tags=["test"],
            created_at="2024-01-01T00:00:00"
        )
        
        assert response.name == "test_tool"
        assert response.description == "Test description"
        assert response.is_async is False
        assert response.tags == ["test"]
    
    def test_tool_list_response(self):
        """Test ToolListResponse."""
        response = ToolListResponse(
            tools=["tool1", "tool2"],
            count=2
        )
        
        assert response.tools == ["tool1", "tool2"]
        assert response.count == 2


class TestToolServiceHost:
    """Test ToolServiceHost functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registry().clear()
        # Clear any existing singleton
        ToolServiceHost._instance = None
    
    def test_service_host_singleton(self):
        """Test that ToolServiceHost is singleton."""
        config = ServiceConfiguration(port=8001)
        host1 = ToolServiceHost(config)
        host2 = ToolServiceHost()
        
        assert host1 is host2
        assert host1.config.port == 8001  # Config from first instance
    
    def test_service_host_configuration(self):
        """Test service host configuration."""
        config = ServiceConfiguration(host="localhost", port=9001)
        host = ToolServiceHost(config)
        
        assert host.config.host == "localhost"
        assert host.config.port == 9001
        assert host.app.title == "AgentHub Tool Service"
    
    def test_get_service_url(self):
        """Test getting service URL."""
        config = ServiceConfiguration(host="192.168.1.1", port=8080)
        host = ToolServiceHost(config)
        
        url = host.get_service_url()
        assert url == "http://192.168.1.1:8080"
    
    def test_is_running_initial_state(self):
        """Test initial running state."""
        host = ToolServiceHost()
        assert host.is_running() is False
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    def test_parameter_validation_success(self, mock_server):
        """Test successful parameter validation."""
        def test_func(x: int, y: str = "default") -> str:
            return f"{x}_{y}"
        
        host = ToolServiceHost()
        
        # Test valid parameters
        params = {"x": 42, "y": "test"}
        validated = host._validate_parameters(test_func, params)
        
        assert validated == {"x": 42, "y": "test"}
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    def test_parameter_validation_missing_required(self, mock_server):
        """Test parameter validation with missing required parameter."""
        def test_func(x: int, y: str) -> str:
            return f"{x}_{y}"
        
        host = ToolServiceHost()
        
        # Test missing required parameter
        params = {"x": 42}
        
        with pytest.raises(ValueError, match="Missing required parameter: y"):
            host._validate_parameters(test_func, params)
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    def test_parameter_validation_unexpected_params(self, mock_server):
        """Test parameter validation with unexpected parameters."""
        def test_func(x: int) -> str:
            return str(x)
        
        host = ToolServiceHost()
        
        # Test unexpected parameters
        params = {"x": 42, "unexpected": "value"}
        
        with pytest.raises(ValueError, match="Unexpected parameters: unexpected"):
            host._validate_parameters(test_func, params)
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    def test_parameter_validation_optional_params(self, mock_server):
        """Test parameter validation with optional parameters."""
        def test_func(x: int, y: str = "default") -> str:
            return f"{x}_{y}"
        
        host = ToolServiceHost()
        
        # Test with only required parameter
        params = {"x": 42}
        validated = host._validate_parameters(test_func, params)
        
        assert validated == {"x": 42}
        # Optional parameter should be handled by Python's default mechanism


@pytest.mark.asyncio
class TestAsyncToolExecution:
    """Test async tool execution functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registry().clear()
        ToolServiceHost._instance = None
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execute_sync_tool(self, mock_server):
        """Test executing synchronous tool."""
        @tool(name="sync_tool")
        def sync_tool(x: int) -> int:
            return x * 2
        
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={"x": 5})
        
        response = await host._execute_tool_endpoint("sync_tool", request)
        
        assert response.success is True
        assert response.result == 10
        assert response.error is None
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execute_async_tool(self, mock_server):
        """Test executing asynchronous tool."""
        @tool(name="async_tool")
        async def async_tool(x: int) -> int:
            await asyncio.sleep(0.001)  # Minimal delay
            return x * 3
        
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={"x": 4})
        
        response = await host._execute_tool_endpoint("async_tool", request)
        
        assert response.success is True
        assert response.result == 12
        assert response.error is None
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execute_nonexistent_tool(self, mock_server):
        """Test executing non-existent tool."""
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={})
        
        response = await host._execute_tool_endpoint("nonexistent", request)
        
        assert response.success is False
        assert response.result is None
        assert "not found" in response.error
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execute_tool_with_error(self, mock_server):
        """Test executing tool that raises an error."""
        @tool(name="error_tool")
        def error_tool():
            raise ValueError("Test error")
        
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={})
        
        response = await host._execute_tool_endpoint("error_tool", request)
        
        assert response.success is False
        assert response.result is None
        assert "Test error" in response.error
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execute_tool_parameter_validation_error(self, mock_server):
        """Test executing tool with parameter validation error."""
        @tool(name="param_tool")
        def param_tool(required_param: str) -> str:
            return required_param.upper()
        
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={})  # Missing required param
        
        response = await host._execute_tool_endpoint("param_tool", request)
        
        assert response.success is False
        assert response.result is None
        assert "validation failed" in response.error.lower()
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    async def test_execution_time_recording(self, mock_server):
        """Test that execution time is recorded."""
        @tool(name="timed_tool")
        def timed_tool() -> str:
            time.sleep(0.01)  # Small delay
            return "completed"
        
        host = ToolServiceHost()
        request = ToolExecutionRequest(parameters={})
        
        response = await host._execute_tool_endpoint("timed_tool", request)
        
        assert response.success is True
        assert response.execution_time > 0.0
        assert response.execution_time < 1.0  # Should be very quick


class TestGlobalServiceFunctions:
    """Test global service management functions."""
    
    def setup_method(self):
        """Setup for each test."""
        # Stop any existing service
        stop_tool_service()
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Ensure service is stopped
        stop_tool_service()
    
    def test_global_service_initial_state(self):
        """Test initial state of global service."""
        assert get_global_service_host() is None
        assert is_service_running() is False
    
    @patch('agentmanager.core.tool_service_host.ToolServiceHost.start')
    def test_start_tool_service(self, mock_start):
        """Test starting global tool service."""
        service = start_tool_service(port=8002, host="localhost")
        
        assert service is not None
        assert get_global_service_host() is service
        mock_start.assert_called_once_with(background=False)
    
    @patch('agentmanager.core.tool_service_host.ToolServiceHost.start')
    def test_start_tool_service_background(self, mock_start):
        """Test starting global tool service in background."""
        service = start_tool_service(port=8003, background=True)
        
        assert service is not None
        mock_start.assert_called_once_with(background=True)
    
    @patch('agentmanager.core.tool_service_host.ToolServiceHost.start')
    @patch('agentmanager.core.tool_service_host.ToolServiceHost.is_running', return_value=True)
    def test_start_already_running_service(self, mock_is_running, mock_start):
        """Test starting service when already running."""
        # First start
        start_tool_service(port=8004)
        
        # Second start should return existing service
        service2 = start_tool_service(port=8005)
        
        # Should only start once
        assert mock_start.call_count == 1
    
    @patch('agentmanager.core.tool_service_host.ToolServiceHost.stop')
    def test_stop_tool_service(self, mock_stop):
        """Test stopping global tool service."""
        # Start service first
        with patch('agentmanager.core.tool_service_host.ToolServiceHost.start'):
            start_tool_service()
        
        # Stop service
        stop_tool_service()
        
        mock_stop.assert_called_once()
        assert get_global_service_host() is None
    
    def test_stop_tool_service_when_none_running(self):
        """Test stopping service when none is running."""
        # Should not raise exception
        stop_tool_service()
        assert get_global_service_host() is None


class TestServiceIntegration:
    """Test service integration scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        get_global_registry().clear()
        stop_tool_service()
    
    def teardown_method(self):
        """Cleanup after each test."""
        stop_tool_service()
    
    def test_service_with_registered_tools(self):
        """Test service behavior with registered tools."""
        @tool(name="integration_tool")
        def integration_tool(message: str) -> str:
            return f"Processed: {message}"
        
        # Mock the FastAPI app and server to avoid actual HTTP server
        with patch('agentmanager.core.tool_service_host.ToolServiceHost.start'):
            service = start_tool_service(port=8006)
            
            # Verify tool is accessible through service
            registry = get_global_registry()
            assert "integration_tool" in registry.list_tools()
    
    @patch('agentmanager.core.tools.service.uvicorn.Server')
    def test_cleanup_on_stop(self, mock_server):
        """Test proper cleanup when service stops."""
        host = ToolServiceHost()
        
        # Mock thread pool
        mock_thread_pool = Mock()
        host.thread_pool = mock_thread_pool
        
        # Call cleanup
        host._cleanup()
        
        assert host.is_running() is False
        mock_thread_pool.shutdown.assert_called_once_with(wait=False)
