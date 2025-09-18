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
    monitoring: bool | str | object = False,  # New: enable real-time monitoring (bool, str, or MonitoringConfig)
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
        monitoring: Enable real-time monitoring. Can be:
            - bool: True/False to enable/disable basic monitoring
            - str: "incremental" or "fullscreen" for display mode
            - MonitoringConfig: Full configuration object
        **kwargs: Additional arguments passed to the agent

    Returns:
        AgentWrapper instance with configured tools and knowledge

    Raises:
        AgentLoadError: If agent cannot be loaded
        ValidationError: If configuration is invalid

    Example:
        >>> # Phase 3 usage with monitoring
        >>> agent = load_agent(
        ...     "agentplug/analysis-agent",
        ...     external_tools=['web_search', 'rag'],
        ...     disabled_builtin_tools=['keyword_extraction'],
        ...     knowledge="You are a data analysis expert.",
        ...     monitoring=True
        ... )
        >>> 
        >>> # Display mode monitoring
        >>> agent = load_agent("agentplug/analysis-agent", monitoring="fullscreen")
        >>> 
        >>> # Full configuration
        >>> from agenthub.monitoring import MonitoringConfig
        >>> config = MonitoringConfig.fullscreen()
        >>> agent = load_agent("agentplug/analysis-agent", monitoring=config)
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
        agent = _create_agent_instance(agent_info, monitoring=_normalize_monitoring_config(monitoring))

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


def _normalize_monitoring_config(monitoring) -> dict:
    """Normalize monitoring configuration to a dictionary."""
    if monitoring is False:
        return {"enabled": False}
    elif monitoring is True:
        return {"enabled": True, "display_mode": "incremental"}
    elif isinstance(monitoring, str):
        if monitoring in ["incremental", "fullscreen"]:
            return {"enabled": True, "display_mode": monitoring}
        else:
            raise ValidationError(f"Invalid monitoring mode: {monitoring}. Use 'incremental' or 'fullscreen'")
    elif hasattr(monitoring, 'display_mode'):  # MonitoringConfig object
        return {
            "enabled": getattr(monitoring, 'enabled', True),
            "display_mode": getattr(monitoring, 'display_mode', 'incremental'),
            "interactive": getattr(monitoring, 'interactive', False),
            "max_memory_mb": getattr(monitoring, 'max_memory_mb', 100),
            "analysis_interval": getattr(monitoring, 'analysis_interval', 2.0),
            "refresh_rate": getattr(monitoring, 'refresh_rate', 1.0),
            "export_format": getattr(monitoring, 'export_format', 'json'),
            "show_metrics": getattr(monitoring, 'show_metrics', True),
            "enable_learning": getattr(monitoring, 'enable_learning', True),
        }
    else:
        raise ValidationError(f"Invalid monitoring configuration type: {type(monitoring)}")


def _create_agent_instance(
    agent_info: dict[str, Any], monitoring: dict = None
) -> AgentWrapper:
    """Create agent instance with enhanced capabilities."""
    from ..core.agents import AgentWrapper
    from ..runtime.agent_runtime import AgentRuntime
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Configure ProcessManager with monitoring setting
    runtime.process_manager.use_dynamic_execution = False
    if monitoring and monitoring.get("enabled", False):
        runtime.process_manager.set_monitoring(True, monitoring)
    else:
        runtime.process_manager.set_monitoring(False)

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
