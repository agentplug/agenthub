"""
Agent Hub - Phase 1 Foundation

A system for executing and managing agentplug agents.
"""

__version__ = "0.1.3"
__author__ = "William"

# Import core modules
import logging

from agenthub import core, runtime, storage
from agenthub.config import AgentHubConfig, get_config, set_config
from agenthub.core.agents import AgentLoader, AgentWrapper
from agenthub.core.logging import get_logger, set_quiet_mode, setup_logging
from agenthub.core.tools import get_tool_metadata
from agenthub.runtime.agent_runtime import AgentRuntime
from agenthub.sdk import get_available_tools, run_resources, tool
from agenthub.sdk.load_agent import load_agent
from agenthub.storage.local_storage import LocalStorage

# Suppress HTTP logs immediately on import
mcp_loggers = [
    "mcp",
    "mcp.client",
    "mcp.client.session",
    "mcp.client.stdio",
    "urllib3",
    "httpx",
    "httpcore",
    "requests",
]
for logger_name in mcp_loggers:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

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
