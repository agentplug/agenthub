"""
Agent Hub - Phase 1 Foundation

A system for executing and managing agentplug agents.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import implemented modules
from agentmanager import core, runtime, storage
from agentmanager.core.agent_loader import AgentLoader
from agentmanager.core.agent_wrapper import AgentWrapper
from agentmanager.runtime.agent_runtime import AgentRuntime
from agentmanager.storage.local_storage import LocalStorage


def load_agent(agent_name):
    """
    Load a pre-created agent from local storage.

    Args:
        agent_name (str): Agent name in format "developer/agent"
                          (e.g., "agentplug/coding-agent")

    Returns:
        AgentWrapper: Wrapped agent ready for method execution
    """
    # Parse agent name
    if "/" not in agent_name:
        raise ValueError(
            f"Agent name must be in format 'developer/agent', got: {agent_name}"
        )

    developer, agent = agent_name.split("/", 1)

    # Initialize components
    storage_manager = LocalStorage()
    runtime_manager = AgentRuntime(storage_manager)
    loader = AgentLoader(storage_manager)

    # Load and wrap agent
    agent_data = loader.load_agent(developer, agent)
    agent_wrapper = AgentWrapper(agent_data, runtime=runtime_manager)

    return agent_wrapper


__all__ = [
    "storage",
    "runtime",
    "core",
    "load_agent",
]
