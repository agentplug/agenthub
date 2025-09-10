"""AgentManager SDK - Simple facade for agent loading and tool injection.

This module provides a clean, user-friendly API that delegates to the enhanced core classes.
"""

from .load_agent import load_agent
from ..core.tools import tool, get_available_tools, run_resources

# Clean, simple API - no complex classes, just functions
__all__ = [
    "load_agent",           # Main function: load_agent(agent, tools=[...])
    "tool",                 # Decorator: @tool(name="...", description="...")
    "get_available_tools",  # List tools: get_available_tools()
    "run_resources",        # Start server: run_resources()
]
