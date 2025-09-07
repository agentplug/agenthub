"""Enhanced load_agent function with tool injection support."""

import os
import json
import subprocess
import sys
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from ..core.tools import get_tool_registry
from ..core.agents import AgentLoader


def load_agent(
    base_agent: str,
    tools: Optional[List[str]] = None,
    **kwargs
):
    """
    Load an agent with optional tool injection capabilities.
    
    Args:
        base_agent: Agent name in format "namespace/agent" (e.g., "agentplug/analysis-agent")
        tools: List of tool names to inject into the agent
        **kwargs: Additional arguments passed to the agent
        
    Returns:
        AgentWrapper instance with tool capabilities
        
    Example:
        >>> agent = load_agent("agentplug/analysis-agent", tools=["web_search"])
        >>> result = agent.execute_tool("web_search", "weather")
    """
    if tools is None:
        tools = []
    
    # Get tool registry
    tool_registry = get_tool_registry()
    
    # Validate tools exist
    available_tools = tool_registry.get_available_tools()
    invalid_tools = [tool for tool in tools if tool not in available_tools]
    if invalid_tools:
        raise ValueError(f"Tools not found: {invalid_tools}. Available tools: {available_tools}")
    
    # Parse agent name to get namespace and agent name
    if "/" not in base_agent:
        raise ValueError(f"Invalid agent name format: {base_agent}. Expected: 'namespace/agent'")
    
    namespace, agent_name = base_agent.split("/", 1)
    
    # Create agent loader with tool registry and storage
    from ..storage.local_storage import LocalStorage
    storage = LocalStorage()
    loader = AgentLoader(storage=storage, tool_registry=tool_registry)
    
    # Load agent using namespace/name format
    agent_info = loader.load_agent(namespace, agent_name)
    if not agent_info.get("valid", False):
        raise ValueError(f"Invalid agent: {base_agent}")
    
    # Assign tools if provided
    agent_id = f"{namespace}/{agent_name}"
    if tools:
        from ..core.tools import assign_tools_to_agent
        assign_tools_to_agent(agent_id, tools)
        print(f"🔐 Assigned tools to agent '{agent_id}': {tools}")
    
    # Create agent wrapper with tool capabilities
    from ..core.agents import AgentWrapper
    agent_wrapper = AgentWrapper(agent_info, tool_registry=tool_registry, agent_id=agent_id, assigned_tools=tools)
    
    return agent_wrapper
