"""Loader for built-in tools."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..registry import ToolRegistry


def load_all_builtin_tools(registry: "ToolRegistry") -> None:
    """Load all built-in tools into the main registry.
    
    Args:
        registry: The main tool registry to register tools with
    """
    # Import and register web tools
    from .web.search import web_search
    registry.register_tool(web_search)
    
    # Import and register data tools
    from .data.files import file_operations
    registry.register_tool(file_operations)
    
    # Import and register AI tools
    from .ai.rag import rag_query
    registry.register_tool(rag_query)
    
    # Import and register system tools
    from .system.shell import shell_command
    registry.register_tool(shell_command)
