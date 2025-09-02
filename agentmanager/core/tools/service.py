"""HTTP service host for AgentHub tools.

This module provides FastAPI-based HTTP service for hosting registered tools
with auto-generated REST API endpoints.
"""

import asyncio
import inspect
import json
import logging
import threading
import time
import warnings
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.*")

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from .decorators import ToolRegistry, ToolMetadata, get_global_registry
from .registry import get_registered_tools_global

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfiguration:
    """Configuration for the tool service host."""
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    workers: int = 1
    thread_pool_max_workers: int = 10


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    execution_id: Optional[str] = None


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    result: Optional[Any] = None
    execution_time: float
    execution_id: Optional[str] = None
    error: Optional[str] = None


class ToolInfoResponse(BaseModel):
    """Response model for tool information."""
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    is_async: bool
    tags: List[str]
    created_at: str


class ToolListResponse(BaseModel):
    """Response model for tool listing."""
    tools: List[str]
    count: int


class ToolServiceHost:
    """FastAPI-based HTTP service for registered tools."""
    
    _instance: Optional["ToolServiceHost"] = None
    
    def __new__(cls, config: Optional[ServiceConfiguration] = None) -> "ToolServiceHost":
        if cls._instance is None:
            cls._instance = super(ToolServiceHost, cls).__new__(cls)
            cls._instance.config = config if config is not None else ServiceConfiguration()
            cls._instance.app = FastAPI(
                title="AgentHub Tool Service",
                description="HTTP API for registered tools",
                version="2.5.0",
            )
            cls._instance.thread_pool = ThreadPoolExecutor(
                max_workers=cls._instance.config.thread_pool_max_workers
            )
            cls._instance._is_running = False
            cls._instance._server_thread: Optional[threading.Thread] = None
            cls._instance._uvicorn_config: Optional[uvicorn.Config] = None
            cls._instance._uvicorn_server: Optional[uvicorn.Server] = None
            cls._instance._setup_routes()
        return cls._instance
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes for tool service."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.get("/tools/", response_model=ToolListResponse)
        async def list_tools():
            """List all registered tools."""
            registry = get_global_registry()
            tool_names = registry.list_tools()
            return ToolListResponse(tools=tool_names, count=len(tool_names))
        
        @self.app.get("/tools/{tool_name}", response_model=ToolInfoResponse)
        async def get_tool_info(tool_name: str):
            """Get information about a specific tool."""
            registry = get_global_registry()
            metadata = registry.get_tool(tool_name)
            
            if metadata is None:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            return ToolInfoResponse(
                name=metadata.name,
                description=metadata.description,
                parameters=metadata.parameters,
                return_type=str(metadata.return_type) if metadata.return_type else "None",
                is_async=metadata.is_async,
                tags=metadata.tags,
                created_at=metadata.created_at.isoformat()
            )
        
        @self.app.post("/tools/{tool_name}/execute", response_model=ToolExecutionResponse)
        async def execute_tool(tool_name: str, request: ToolExecutionRequest):
            """Execute a tool with provided parameters."""
            return await self._execute_tool_endpoint(tool_name, request)
    
    async def _execute_tool_endpoint(
        self, 
        tool_name: str, 
        request: ToolExecutionRequest
    ) -> ToolExecutionResponse:
        """Execute tool endpoint implementation."""
        start_time = time.time()
        
        try:
            # Get tool function
            registry = get_global_registry()
            tool_func = registry.get_function(tool_name)
            
            if tool_func is None:
                execution_time = time.time() - start_time
                return ToolExecutionResponse(
                    success=False,
                    result=None,
                    execution_time=execution_time,
                    execution_id=request.execution_id,
                    error=f"Tool '{tool_name}' not found",
                )
            
            # Validate parameters
            try:
                validated_params = self._validate_parameters(tool_func, request.parameters)
            except ValueError as validation_error:
                execution_time = time.time() - start_time
                logger.warning(f"Parameter validation failed for {tool_name}: {validation_error}")
                return ToolExecutionResponse(
                    success=False,
                    result=None,
                    execution_time=execution_time,
                    execution_id=request.execution_id,
                    error=f"Parameter validation failed: {str(validation_error)}",
                )
            
            # Execute tool
            try:
                if inspect.iscoroutinefunction(tool_func):
                    result = await tool_func(**validated_params)
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.thread_pool, 
                        lambda: tool_func(**validated_params)
                    )
                
                execution_time = time.time() - start_time
                logger.info(f"Tool {tool_name} executed successfully in {execution_time:.3f}s")
                
                return ToolExecutionResponse(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    execution_id=request.execution_id,
                )
                
            except Exception as exec_error:
                execution_time = time.time() - start_time
                error_msg = f"Tool execution failed: {str(exec_error)}"
                logger.error(f"Execution error for {tool_name}: {error_msg}")
                
                return ToolExecutionResponse(
                    success=False,
                    result=None,
                    execution_time=execution_time,
                    execution_id=request.execution_id,
                    error=error_msg,
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error in tool execution for {tool_name}: {error_msg}")
            
            return ToolExecutionResponse(
                success=False,
                result=None,
                execution_time=execution_time,
                execution_id=request.execution_id,
                error=error_msg,
            )
    
    def _validate_parameters(self, func: Callable[..., Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare parameters for function execution."""
        try:
            signature = inspect.signature(func)
            validated_params = {}
            
            # Check for required parameters
            for param_name, param in signature.parameters.items():
                if param_name in params:
                    validated_params[param_name] = params[param_name]
                elif param.default == param.empty:
                    raise ValueError(f"Missing required parameter: {param_name}")
                # Optional parameters with defaults are handled automatically by Python
            
            # Check for unexpected parameters
            extra_params = set(params.keys()) - set(signature.parameters.keys())
            if extra_params:
                raise ValueError(f"Unexpected parameters: {', '.join(extra_params)}")
            
            return validated_params
            
        except Exception as e:
            raise ValueError(f"Parameter validation error: {str(e)}") from e
    
    def start(self, background: bool = False) -> None:
        """Start the tool service."""
        if self._is_running:
            logger.warning("Tool service is already running")
            return
        
        self._uvicorn_config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            access_log=False,  # Reduce noise
        )
        
        if background:
            self._start_background()
        else:
            self._start_foreground()
    
    def _start_foreground(self) -> None:
        """Start service in foreground (blocking)."""
        self._is_running = True
        self._uvicorn_server = uvicorn.Server(self._uvicorn_config)
        
        try:
            logger.info(f"Starting tool service on {self.config.host}:{self.config.port}")
            self._uvicorn_server.run()
        except Exception as e:
            logger.error(f"Service startup failed: {e}")
            self._is_running = False
        finally:
            self._cleanup()
    
    def _start_background(self) -> None:
        """Start service in background thread."""
        def _run_server():
            self._is_running = True
            self._uvicorn_server = uvicorn.Server(self._uvicorn_config)
            
            try:
                logger.info(f"Starting tool service on {self.config.host}:{self.config.port}")
                self._uvicorn_server.run()
            except Exception as e:
                logger.error(f"Service startup failed: {e}")
            finally:
                self._is_running = False
                self._cleanup()
        
        self._server_thread = threading.Thread(target=_run_server, daemon=True)
        self._server_thread.start()
        
        # Wait for service to start
        max_wait = 10
        wait_time = 0
        while not self._is_running and wait_time < max_wait:
            time.sleep(0.1)
            wait_time += 0.1
        
        if not self._is_running:
            raise RuntimeError("Failed to start tool service in background")
    
    def stop(self) -> None:
        """Stop the tool service."""
        if not self._is_running:
            logger.warning("Tool service is not running")
            return
        
        logger.info("Stopping tool service...")
        
        if self._uvicorn_server:
            self._uvicorn_server.should_exit = True
        
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5)
        
        self._cleanup()
        logger.info("Tool service stopped")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        self._is_running = False
        self.thread_pool.shutdown(wait=False)
    
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._is_running
    
    def get_service_url(self) -> str:
        """Get the service URL."""
        return f"http://{self.config.host}:{self.config.port}"


# Global service host instance
_global_service_host: Optional[ToolServiceHost] = None


def start_tool_service(
    port: int = 8000, 
    host: str = "127.0.0.1", 
    background: bool = False
) -> ToolServiceHost:
    """Start the global tool service."""
    global _global_service_host
    
    if _global_service_host is not None and _global_service_host.is_running():
        logger.warning("Tool service is already running")
        return _global_service_host
    
    config = ServiceConfiguration(host=host, port=port)
    _global_service_host = ToolServiceHost(config)
    _global_service_host.start(background=background)
    
    return _global_service_host


def stop_tool_service() -> None:
    """Stop the global tool service."""
    global _global_service_host
    
    if _global_service_host is not None:
        _global_service_host.stop()
        _global_service_host = None


def get_global_service_host() -> Optional[ToolServiceHost]:
    """Get the global service host instance."""
    return _global_service_host


def is_service_running() -> bool:
    """Check if the global service is running."""
    return _global_service_host is not None and _global_service_host.is_running()
