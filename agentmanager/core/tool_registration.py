"""Tool registration system for AgentHub.

This module provides the ToolRegistrationManager for explicit tool registration,
including validation and error handling.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .tool_decorators import ToolMetadata, ToolRegistry, get_global_registry, get_tool_metadata

logger = logging.getLogger(__name__)


class ToolRegistrationError(Exception):
    """Custom exception for tool registration failures."""
    pass


@dataclass
class ToolRegistrationResult:
    """Result of a tool registration attempt."""
    success: bool
    tool_name: str
    message: str
    metadata: Optional[ToolMetadata] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ToolRegistrationManager:
    """Manager for explicit tool registration with validation."""
    
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry if registry is not None else get_global_registry()
        self._enable_validation = True
    
    def enable_validation(self, enable: bool) -> None:
        """Enable or disable validation during registration."""
        self._enable_validation = enable
    
    def register_function(
        self,
        func: Callable[..., Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        force: bool = False,
    ) -> ToolRegistrationResult:
        """Register a function as a tool with validation."""
        try:
            tool_name = name or getattr(func, '__name__', 'unknown')
            
            # Check if tool already exists
            if not force and self.registry.get_tool(tool_name) is not None:
                return ToolRegistrationResult(
                    success=False,
                    tool_name=tool_name,
                    message=f"Tool '{tool_name}' already registered. Use force=True to override.",
                    errors=[f"Duplicate tool name: {tool_name}"]
                )
            
            # Basic function validation
            if not callable(func):
                return ToolRegistrationResult(
                    success=False,
                    tool_name=tool_name,
                    message="Object is not callable",
                    errors=["Function must be callable"]
                )
            
            if not hasattr(func, '__name__'):
                return ToolRegistrationResult(
                    success=False,
                    tool_name=tool_name,
                    message="Function does not have a name",
                    errors=["Function must have __name__ attribute"]
                )
            
            # Get or create metadata
            metadata = get_tool_metadata(func)
            if metadata is None:
                # Create metadata manually if not decorated
                from .tool_decorators import _extract_function_metadata
                import inspect
                
                parameters = _extract_function_metadata(func)
                return_type = inspect.signature(func).return_annotation
                if return_type == inspect.Signature.empty:
                    return_type = None
                
                metadata = ToolMetadata(
                    name=tool_name,
                    description=description or (func.__doc__ or "").strip() or f"Tool: {tool_name}",
                    function=func,
                    parameters=parameters,
                    return_type=return_type,
                    is_async=inspect.iscoroutinefunction(func),
                    tags=tags or [],
                )
            
            # Register the tool
            if force and self.registry.get_tool(tool_name) is not None:
                # Clear existing registration for force override
                self.registry._tools.pop(tool_name, None)
                self.registry._tool_functions.pop(tool_name, None)
            
            self.registry.register(metadata)
            
            logger.info(f"Successfully registered tool: {tool_name}")
            return ToolRegistrationResult(
                success=True,
                tool_name=tool_name,
                message=f"Tool '{tool_name}' registered successfully",
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = f"Registration failed for {getattr(func, '__name__', 'unknown')}: {str(e)}"
            logger.error(error_msg)
            return ToolRegistrationResult(
                success=False,
                tool_name=getattr(func, '__name__', 'unknown'),
                message=error_msg,
                errors=[str(e)]
            )
    
    def register_multiple(
        self,
        functions: List[Callable[..., Any]],
        force: bool = False
    ) -> List[ToolRegistrationResult]:
        """Register multiple functions as tools."""
        results = []
        for func in functions:
            result = self.register_function(func, force=force)
            results.append(result)
        return results
    
    def get_registered_tools(self) -> List[ToolMetadata]:
        """Get all registered tool metadata."""
        return list(self.registry.get_all_metadata().values())
    
    def is_tool_registered(self, name: str) -> bool:
        """Check if a tool is registered."""
        return self.registry.get_tool(name) is not None
    
    def get_tool_function(self, name: str) -> Optional[Callable[..., Any]]:
        """Get tool function by name."""
        return self.registry.get_function(name)
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self.registry._tools:
            del self.registry._tools[name]
            del self.registry._tool_functions[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False
    
    def clear_all(self) -> None:
        """Clear all registered tools."""
        self.registry.clear()
        logger.info("Cleared all registered tools")


# Global registration manager instance
_global_registration_manager = ToolRegistrationManager()


def register_tools(
    tools: List[Callable[..., Any]], 
    force: bool = False
) -> List[ToolRegistrationResult]:
    """Register multiple tools using the global manager."""
    return _global_registration_manager.register_multiple(tools, force=force)


def register_function(
    func: Callable[..., Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    force: bool = False,
) -> ToolRegistrationResult:
    """Register a single function using the global manager."""
    return _global_registration_manager.register_function(
        func, name=name, description=description, tags=tags, force=force
    )


def get_registered_tools_global() -> List[ToolMetadata]:
    """Get all registered tools from global manager."""
    return _global_registration_manager.get_registered_tools()


def is_tool_registered_global(name: str) -> bool:
    """Check if tool is registered in global manager."""
    return _global_registration_manager.is_tool_registered(name)


def get_tool_function_global(name: str) -> Optional[Callable[..., Any]]:
    """Get tool function from global manager."""
    return _global_registration_manager.get_tool_function(name)


def get_global_registration_manager() -> ToolRegistrationManager:
    """Get the global registration manager instance."""
    return _global_registration_manager
