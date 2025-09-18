"""Enhanced load_agent function with Phase 3 features."""

import warnings
from typing import Any

from ..core.agents import AgentLoader, AgentWrapper
from ..core.tools import get_tool_registry
from ..core.tools.exceptions import AgentLoadError, ValidationError


def load_agent(
    base_agent: str,
    tools: list[str] | None = None,  # DEPRECATED: use external_tools instead
    external_tools: list[str] | None = None,  # New: external tools
    disabled_builtin_tools: list[str] | None = None,  # New: disable built-in tools
    knowledge: str | None = None,  # New: inject knowledge
    **kwargs,
) -> AgentWrapper:
    """
    Load agent with user-friendly Phase 3 configuration.

    Args:
        base_agent: Agent name in format "namespace/agent"
        tools: DEPRECATED - use external_tools instead (for backward compatibility)
        external_tools: List of external tool names to add
        disabled_builtin_tools: List of built-in tools to disable
        knowledge: Text knowledge to inject into agent context
        **kwargs: Additional arguments passed to the agent

    Returns:
        AgentWrapper instance with configured tools and knowledge

    Raises:
        AgentLoadError: If agent cannot be loaded
        ValidationError: If configuration is invalid

    Example:
        >>> # Phase 3 usage
        >>> agent = load_agent(
        ...     "agentplug/analysis-agent",
        ...     external_tools=['web_search', 'rag'],
        ...     disabled_builtin_tools=['keyword_extraction'],
        ...     knowledge="You are a data analysis expert."
        ... )
        >>>
        >>> # Backward compatibility
        >>> agent = load_agent("agentplug/analysis-agent", tools=['web_search'])
    """
    # Handle backward compatibility
    if tools is not None:
        if external_tools is not None:
            raise ValidationError(
                "Cannot specify both 'tools' and 'external_tools'. "
                "Use 'external_tools' instead."
            )
        external_tools = tools
        warnings.warn(
            "'tools' parameter is deprecated. Use 'external_tools' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    try:
        # Load agent definition from YAML (developer created)
        agent_info = _load_agent_from_yaml(base_agent)

        # Create agent instance
        agent = _create_agent_instance(agent_info)

        # Apply user configuration
        if external_tools:
            agent.add_external_tools(external_tools)

        if disabled_builtin_tools:
            agent.disable_builtin_tools(disabled_builtin_tools)

        if knowledge:
            agent.inject_knowledge(knowledge)

        return agent

    except Exception as e:
        raise AgentLoadError(f"Failed to load agent '{base_agent}': {e}") from e


def _load_agent_from_yaml(agent_name: str) -> dict[str, Any]:
    """Load agent definition from YAML with enhanced schema support."""
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    loader = AgentLoader(storage=storage)

    # Parse namespace/agent format
    if "/" in agent_name:
        namespace, name = agent_name.split("/", 1)
    else:
        namespace, name = "default", agent_name

    agent_info = loader.load_agent(namespace, name)
    if not agent_info.get("valid", False):
        raise AgentLoadError(f"Invalid agent: {agent_name}")

    return agent_info


def _create_agent_instance(agent_info: dict[str, Any]) -> AgentWrapper:
    """Create agent instance with enhanced capabilities."""
    from ..core.agents import AgentWrapper
    from ..runtime.agent_runtime import AgentRuntime
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)
    runtime.process_manager.use_dynamic_execution = False

    # Parse agent ID
    namespace = agent_info.get("namespace", "unknown")
    name = agent_info.get("name", "unknown")
    agent_id = f"{namespace}/{name}"

    return AgentWrapper(
        agent_info=agent_info,
        runtime=runtime,
        tool_registry=get_tool_registry(),
        agent_id=agent_id,
    )
