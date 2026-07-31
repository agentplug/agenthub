"""AgentHub - The App Store for AI Agents.

Discover, install, and use AI agents with one line of code.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

try:
    __version__ = _package_version("agenthub-sdk")
except PackageNotFoundError:
    # Source checkout without an installed distribution
    __version__ = "0.0.0+unknown"

__author__ = "William"

# Import core modules
from agenthub import core, runtime, storage
from agenthub.config import AgentHubConfig, get_config, set_config
from agenthub.core.agents import AgentLoader, AgentWrapper
from agenthub.core.logging import get_logger, set_quiet_mode, setup_logging
from agenthub.core.tools import get_tool_metadata
from agenthub.runtime.agent_runtime import AgentRuntime
from agenthub.sdk import get_available_tools, run_resources, tool
from agenthub.sdk.load_agent import load_agent
from agenthub.storage.local_storage import LocalStorage

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
