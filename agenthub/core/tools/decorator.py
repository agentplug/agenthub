"""Tool decorator for Phase 2.5."""

from collections.abc import Callable

from .registry import _registry


def tool(name: str, description: str = "", namespace: str = "custom") -> Callable:
    """
    Decorator for registering functions as tools.

    Args:
        name: Tool name (must be unique)
        description: Tool description
        namespace: Tool namespace (default: "custom")

    Returns:
        Decorated function

    Example:
        @tool(name="my_tool", description="My custom tool")
        def my_function(data: str) -> dict:
            return {"result": data}
    """

    def decorator(func: Callable) -> Callable:
        """Register the function as a tool."""
        return _registry.register_tool(name, func, description, namespace)

    return decorator
