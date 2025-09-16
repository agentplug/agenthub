"""Enhanced load_agent function with tool injection support."""

from ..core.agents import AgentLoader
from ..core.tools import get_tool_registry


def load_agent(base_agent: str, tools: list[str] | None = None, **kwargs):
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
        raise ValueError(
            f"Tools not found: {invalid_tools}. Available tools: {available_tools}"
        )

    # Parse agent name to get namespace and agent name
    if "/" not in base_agent:
        raise ValueError(
            f"Invalid agent name format: {base_agent}. Expected: 'namespace/agent'"
        )

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

    # Create agent wrapper with tool capabilities and runtime
    from ..core.agents import AgentWrapper
    from ..runtime.agent_runtime import AgentRuntime

    # Create runtime with subprocess execution for proper environment isolation
    runtime = AgentRuntime(storage=storage)
    runtime.process_manager.use_dynamic_execution = False

    agent_wrapper = AgentWrapper(
        agent_info,
        tool_registry=tool_registry,
        agent_id=agent_id,
        assigned_tools=tools,
        runtime=runtime,
    )

    # Inject tool context into the agent
    if tools:
        agent_wrapper.inject_tool_context()

    return agent_wrapper
