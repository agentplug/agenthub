"""
Agent Hub - Phase 1 Foundation

A system for executing and managing agentplug agents.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import implemented modules
from agentmanager import core, runtime, storage
from agentmanager.core.agents import AgentLoader, AgentWrapper
from agentmanager.runtime.agent_runtime import AgentRuntime
from agentmanager.storage.local_storage import LocalStorage

# Import SDK functionality
from agentmanager.sdk import load_agent as enhanced_load_agent, tool, get_available_tools, run_resources


def load_agent(agent_name, tools=None, setup_environment=True):
    """
    Load an agent, automatically installing it if it doesn't exist.
    
    This is the recommended way to use agents - just call this function
    and it will handle everything automatically!

    Args:
        agent_name (str): Agent name in format "developer/agent"
                          (e.g., "agentplug/scientific-paper-analyzer")
        tools (list, optional): List of tool names to inject into the agent
        setup_environment (bool): Whether to set up virtual environment and install dependencies

    Returns:
        AgentWrapper or EnhancedAgent: Wrapped agent ready for method execution

    Raises:
        ValueError: If agent name format is invalid
        RuntimeError: If agent installation fails
    """
    # If tools are provided, use enhanced load_agent
    if tools is not None:
        return enhanced_load_agent(agent_name, tools=tools)
    
    # Otherwise, use the original load_agent logic
    # Parse agent name
    if "/" not in agent_name:
        raise ValueError(f"Invalid agent name format: {agent_name}. Expected: 'developer/agent'")

    developer, agent = agent_name.split("/", 1)

    # Initialize managers
    storage_manager = LocalStorage()
    runtime_manager = AgentRuntime(storage_manager)
    loader = AgentLoader(storage_manager)

    # Check if agent exists
    if not storage_manager.agent_exists(developer, agent):
        print(f"📥 Agent '{agent_name}' not found. Installing automatically...")

        # Import and use AutoInstaller
        from agentmanager.github.auto_installer import AutoInstaller

        installer = AutoInstaller(setup_environment=setup_environment)
        result = installer.install_agent(agent_name)

        if not result.success:
            raise RuntimeError(f"Failed to install agent '{agent_name}': {result.error_message}")

        print(f"✅ Agent '{agent_name}' installed successfully!")

    # Now load the agent
    agent_data = loader.load_agent(developer, agent)
    agent_wrapper = AgentWrapper(agent_data, runtime=runtime_manager)

    return agent_wrapper


__all__ = [
    "storage",
    "runtime", 
    "core",
    "load_agent",
    "tool",
    "get_available_tools",
    "run_resources",
]
