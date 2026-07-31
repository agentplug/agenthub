"""Enhanced load_agent function with Phase 3 features."""

import logging
import warnings
from typing import Any

from ..core.agents import AgentLoader, AgentWrapper
from ..core.agents.loader import AgentLoadError, AgentNotFoundError
from ..core.tools import get_tool_registry
from ..core.tools.exceptions import ValidationError

logger = logging.getLogger(__name__)


def load_agent(
    base_agent: str,
    tools: list[str] | None = None,  # DEPRECATED: use external_tools instead
    external_tools: list[str] | None = None,  # New: external tools
    disabled_builtin_tools: list[str] | None = None,  # New: disable built-in tools
    knowledge: str | None = None,  # New: inject knowledge
    monitoring: bool = False,  # New: enable real-time monitoring
    **kwargs: Any,
) -> AgentWrapper:
    """
    Load agent with user-friendly Phase 3 configuration.

    Args:
        base_agent: Agent name in format "namespace/agent"
        tools: DEPRECATED - use external_tools instead (for backward compatibility)
        external_tools: List of external tool names to add
        disabled_builtin_tools: List of built-in tools to disable
        knowledge: Text knowledge to inject into agent context
        monitoring: Enable real-time monitoring (default: False)
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

    # A spec may pin a ref ("user/agent@sha"); local lookups use the clean
    # name, installation receives the full spec
    from ..github.url_parser import parse_agent_spec

    clean_name, _ref = parse_agent_spec(base_agent)

    # Try to load agent definition from YAML first; a missing agent (typed,
    # not string-matched) triggers auto-installation
    try:
        agent_info = _load_agent_from_yaml(clean_name)
    except AgentNotFoundError:
        logger.info(
            f"🤖 Agent '{base_agent}' not found locally. "
            f"Attempting to auto-install..."
        )
        try:
            agent_info = _auto_install_agent(base_agent)
        except Exception as install_error:
            raise AgentLoadError(
                f"Failed to auto-install agent '{base_agent}': {install_error}"
            ) from install_error

    try:
        # Create agent instance
        agent = _create_agent_instance(agent_info, monitoring=monitoring)

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


def _auto_install_agent(agent_name: str) -> dict[str, Any]:
    """Auto-install an agent if it's not found locally."""
    from ..github.auto_installer import AutoInstaller

    # Create auto-installer
    installer = AutoInstaller()

    # Install the agent
    result = installer.install_agent(agent_name)

    if not result.success:
        raise AgentLoadError(
            f"Failed to auto-install agent '{agent_name}': {result.error_message}"
        )

    logger.info(f"✅ Successfully installed agent '{agent_name}'!")
    logger.info(f"📁 Location: {result.local_path}")

    # Load the newly installed agent (lookup by clean name; the spec may
    # have carried an @ref pin)
    from ..github.url_parser import parse_agent_spec

    clean_name, _ref = parse_agent_spec(agent_name)
    return _load_agent_from_yaml(clean_name)


def _create_agent_instance(
    agent_info: dict[str, Any], monitoring: bool = False
) -> AgentWrapper:
    """Create agent instance with enhanced capabilities."""
    from ..core.agents import AgentWrapper
    from ..runtime.agent_runtime import AgentRuntime
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Configure ProcessManager with monitoring setting
    runtime.process_manager.use_dynamic_execution = False
    runtime.process_manager.set_monitoring(monitoring)

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
