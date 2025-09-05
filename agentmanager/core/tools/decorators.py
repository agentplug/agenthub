"""Tool decorator system for AgentHub.

This module provides decorators for tool registration and metadata extraction.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime


F = TypeVar('F', bound=Callable[..., Any])


@dataclass(frozen=True)
class ToolMetadata:
    """Metadata for a registered tool."""

    name: str
    description: str
    function: Callable[..., Any]
    parameters: Dict[str, Any]
    return_type: Optional[type]
    created_at: datetime = field(default_factory=datetime.now)
    is_async: bool = False
    tags: List[str] = field(default_factory=list)
    input_schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "return_type": str(self.return_type) if self.return_type else None,
            "created_at": self.created_at.isoformat(),
            "is_async": self.is_async,
            "tags": self.tags,
            "input_schema": self.input_schema,
        }


# Note: ToolRegistry moved to registry.py for better separation of concerns


def _extract_function_metadata(func: Callable[..., Any]) -> Dict[str, Any]:
    """Extract parameter metadata from function signature."""
    signature = inspect.signature(func)
    parameters = {}

    for name, param in signature.parameters.items():
        param_info = {
            "name": name,
            "annotation": str(param.annotation) if param.annotation != param.empty else None,
            "default": param.default if param.default != param.empty else None,
            "kind": param.kind.name,
        }
        parameters[name] = param_info

    return parameters


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    auto_register: bool = True,
    input_schema: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """Decorator to mark a function as a tool."""
    if tags is None:
        tags = []

    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip()

        # Extract function metadata
        parameters = _extract_function_metadata(func)
        return_type = inspect.signature(func).return_annotation
        if return_type == inspect.Signature.empty:
            return_type = None

        is_async = inspect.iscoroutinefunction(func)

        # Create metadata
        metadata = ToolMetadata(
            name=tool_name,
            description=tool_description,
            function=func,
            parameters=parameters,
            return_type=return_type,
            is_async=is_async,
            tags=tags.copy(),
            input_schema=input_schema,
        )

        # Store metadata as function attribute
        func.__tool_metadata__ = metadata  # type: ignore

        # Auto-register if requested
        if auto_register:
            from .registry import get_global_registry
            get_global_registry().register(metadata)

        return func

    return decorator


def register_tool(func: F) -> F:
    """Decorator to register a function as a tool with automatic metadata extraction."""
    return tool()(func)


def get_tool_metadata(func: Callable[..., Any]) -> Optional[ToolMetadata]:
    """Get tool metadata from a decorated function."""
    return getattr(func, '__tool_metadata__', None)


def is_tool(func: Callable[..., Any]) -> bool:
    """Check if a function is decorated as a tool."""
    return hasattr(func, '__tool_metadata__')


# Note: ToolDiscovery moved to discovery.py for better separation of concerns
