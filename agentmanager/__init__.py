"""
Agent Hub - Phase 1 Foundation

A system for executing and managing agentplug agents.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import core modules
from agentmanager import core, runtime, storage

# Import configuration
from agentmanager.config import get_config, set_config, AgentHubConfig

# Import centralized logging utilities
from agentmanager.core.logging import setup_logging, get_logger, set_quiet_mode

# Suppress HTTP logs immediately on import
import logging
mcp_loggers = ['mcp', 'mcp.client', 'mcp.client.session', 'mcp.client.stdio', 'urllib3', 'httpx', 'httpcore', 'requests']
for logger_name in mcp_loggers:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

# Import unified loader
from agentmanager.core.loader import load_agent

# Import legacy components for backwards compatibility
from agentmanager.core.agents import AgentLoader, AgentWrapper
from agentmanager.runtime.agent_runtime import AgentRuntime
from agentmanager.storage.local_storage import LocalStorage

# Import SDK functionality
from agentmanager.sdk import tool, get_available_tools, run_resources
from agentmanager.core.tools import get_tool_metadata


__all__ = [
    # Core functionality
    "load_agent",
    "tool", 
    "get_available_tools",
    "run_resources",
    "get_tool_metadata",
    
    # Configuration
    "get_config",
    "set_config", 
    "AgentHubConfig",
    
    # Logging utilities
    "setup_logging",
    "get_logger",
    "set_quiet_mode",
    
    # Modules
    "core",
    "runtime",
    "storage",
    
    # Legacy components (for backwards compatibility)
    "AgentLoader",
    "AgentWrapper", 
    "AgentRuntime",
    "LocalStorage",
]
