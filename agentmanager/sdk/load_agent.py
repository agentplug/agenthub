"""Enhanced load_agent function with tool injection support."""

import os
import json
import subprocess
import sys
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from ..core.tools import get_tool_registry, get_tool_metadata
from ..core.mcp import get_tool_manager, get_tool_injector
from .enhanced_agent import EnhancedAgent


def load_agent(
    base_agent: str,
    tools: Optional[List[str]] = None,
    **kwargs
) -> EnhancedAgent:
    """
    Load an agent with optional tool injection capabilities.
    
    Args:
        base_agent: Path to the agent (e.g., "agentplug/analysis-agent")
        tools: List of tool names to inject into the agent
        **kwargs: Additional arguments passed to the agent
        
    Returns:
        EnhancedAgent instance with tool capabilities
        
    Example:
        >>> agent = load_agent("agentplug/analysis-agent", tools=["web_search"])
        >>> response = agent.analyze_text("What's the weather?")
    """
    if tools is None:
        tools = []
    
    # Get tool registry and manager
    tool_registry = get_tool_registry()
    tool_manager = get_tool_manager()
    tool_injector = get_tool_injector()
    
    # Validate tools exist
    available_tools = tool_registry.get_available_tools()
    invalid_tools = [tool for tool in tools if tool not in available_tools]
    if invalid_tools:
        raise ValueError(f"Tools not found: {invalid_tools}. Available tools: {available_tools}")
    
    # Create enhanced agent
    enhanced_agent = EnhancedAgent(
        base_agent=base_agent,
        assigned_tools=tools,
        tool_registry=tool_registry,
        tool_manager=tool_manager,
        tool_injector=tool_injector,
        **kwargs
    )
    
    return enhanced_agent
