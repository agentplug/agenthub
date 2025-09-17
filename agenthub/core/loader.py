"""Unified agent loader with standardized interface."""

import logging
from dataclasses import dataclass

from agenthub.config import get_config
from agenthub.core.agents import AgentLoader, AgentWrapper
from agenthub.core.common.result import (
    ErrorType,
    Result,
    agent_not_found_error,
    execution_error,
    validation_error,
)
from agenthub.core.tools import assign_tools_to_agent, get_tool_registry
from agenthub.github.auto_installer import AutoInstaller
from agenthub.runtime.agent_runtime import AgentRuntime
from agenthub.storage.local_storage import LocalStorage

logger = logging.getLogger(__name__)


@dataclass
class AgentLoadOptions:
    """Options for loading agents."""

    tools: list[str] | None = None
    setup_environment: bool = True
    auto_install: bool = True
    timeout: int | None = None
    use_subprocess: bool | None = None


class UnifiedAgentLoader:
    """Unified agent loader that handles all agent loading scenarios."""

    def __init__(self):
        """Initialize the unified loader."""
        self.config = get_config()
        self.storage = LocalStorage()
        self.runtime = AgentRuntime(self.storage)
        self.agent_loader = AgentLoader(self.storage)
        self.tool_registry = get_tool_registry()

        # Configure runtime based on config
        self.runtime.process_manager.use_dynamic_execution = (
            not self.config.use_subprocess_execution
        )
        if self.config.default_timeout:
            self.runtime.process_manager.timeout = self.config.default_timeout

    def load(
        self, agent_name: str, options: AgentLoadOptions | None = None
    ) -> Result[AgentWrapper]:
        """
        Load an agent with unified interface.

        Args:
            agent_name: Agent name in format "namespace/agent"
            (e.g., "agentplug/analysis-agent")
            options: Loading options including tools, environment setup, etc.

        Returns:
            Result containing AgentWrapper or error
        """
        if options is None:
            options = AgentLoadOptions()

        # Apply config defaults
        if options.setup_environment is None:
            options.setup_environment = self.config.setup_environment_by_default
        if options.use_subprocess is None:
            options.use_subprocess = self.config.use_subprocess_execution
        if options.timeout is None:
            options.timeout = self.config.default_timeout

        try:
            # Validate agent name format
            if "/" not in agent_name:
                return Result.fail(
                    validation_error(
                        f"Invalid agent name format: {agent_name}. "
                        f"Expected: 'developer/agent-name'",
                        {
                            "agent_name": agent_name,
                            "expected_format": "namespace/agent",
                        },
                    )
                )

            namespace, agent = agent_name.split("/", 1)

            # Check if agent exists
            if not self.storage.agent_exists(namespace, agent):
                if options.auto_install:
                    logger.info(
                        f"Agent '{agent_name}' not found. Installing automatically..."
                    )
                    install_result = self._install_agent(
                        agent_name, options.setup_environment
                    )
                    if install_result.is_err():
                        return install_result
                    logger.info(f"Agent '{agent_name}' installed successfully!")
                else:
                    return Result.fail(
                        agent_not_found_error(
                            agent_name,
                            {
                                "namespace": namespace,
                                "agent": agent,
                                "auto_install": False,
                            },
                        )
                    )

            # Load agent
            try:
                agent_data = self.agent_loader.load_agent(namespace, agent)
            except Exception as e:
                return Result.fail(
                    execution_error(
                        f"Failed to load agent data: {str(e)}",
                        {"namespace": namespace, "agent": agent},
                        cause=e,
                    )
                )

            # Configure runtime settings
            if options.timeout:
                self.runtime.process_manager.timeout = options.timeout
            if options.use_subprocess is not None:
                self.runtime.process_manager.use_dynamic_execution = (
                    not options.use_subprocess
                )

            # Create agent wrapper
            agent_id = f"{namespace}/{agent}"
            agent_wrapper = AgentWrapper(
                agent_data,
                tool_registry=self.tool_registry,
                agent_id=agent_id,
                assigned_tools=options.tools or [],
                runtime=self.runtime,
            )

            # Assign tools if provided
            if options.tools:
                validation_result = self._validate_and_assign_tools(
                    agent_id, options.tools
                )
                if validation_result.is_err():
                    return validation_result

            logger.info(
                f"Successfully loaded agent '{agent_name}' with "
                f"{len(options.tools or [])} tools"
            )
            return Result.ok(agent_wrapper)

        except Exception as e:
            logger.error(f"Unexpected error loading agent '{agent_name}': {e}")
            return Result.fail(
                execution_error(
                    f"Unexpected error loading agent: {str(e)}",
                    {"agent_name": agent_name},
                    cause=e,
                )
            )

    def _install_agent(self, agent_name: str, setup_environment: bool) -> Result[None]:
        """Install an agent automatically."""
        try:
            installer = AutoInstaller(setup_environment=setup_environment)
            result = installer.install_agent(agent_name)

            if not result.success:
                return Result.fail(
                    execution_error(
                        f"Failed to install agent '{agent_name}': "
                        f"{result.error_message}",
                        {
                            "agent_name": agent_name,
                            "installer_error": result.error_message,
                        },
                    )
                )

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                execution_error(
                    f"Installation failed for agent '{agent_name}': {str(e)}",
                    {"agent_name": agent_name},
                    cause=e,
                )
            )

    def _validate_and_assign_tools(
        self, agent_id: str, tools: list[str]
    ) -> Result[None]:
        """Validate and assign tools to an agent."""
        try:
            # Get available tools
            available_tools = self.tool_registry.get_available_tools()

            # Check for invalid tools
            invalid_tools = [tool for tool in tools if tool not in available_tools]
            if invalid_tools:
                return Result.fail(
                    validation_error(
                        f"Tools not found: {invalid_tools}",
                        {
                            "invalid_tools": invalid_tools,
                            "available_tools": available_tools,
                            "agent_id": agent_id,
                        },
                    )
                )

            # Assign tools to agent
            assign_tools_to_agent(agent_id, tools)
            logger.info(f"Assigned tools to agent '{agent_id}': {tools}")

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                execution_error(
                    f"Failed to assign tools to agent '{agent_id}': {str(e)}",
                    {"agent_id": agent_id, "tools": tools},
                    cause=e,
                )
            )


# Global loader instance
_loader: UnifiedAgentLoader | None = None


def get_loader() -> UnifiedAgentLoader:
    """Get the global unified loader instance."""
    global _loader
    if _loader is None:
        _loader = UnifiedAgentLoader()
    return _loader


def load_agent(
    agent_name: str,
    tools: list[str] | None = None,
    setup_environment: bool = True,
    auto_install: bool = True,
    timeout: int | None = None,
    use_subprocess: bool | None = None,
) -> AgentWrapper:
    """
    Unified agent loading function.

    Args:
        agent_name: Agent name in format "namespace/agent"
        tools: List of tool names to assign to the agent
        setup_environment: Whether to set up virtual environment
        auto_install: Whether to auto-install missing agents
        timeout: Execution timeout in seconds
        use_subprocess: Whether to use subprocess execution

    Returns:
        AgentWrapper instance ready for execution

    Raises:
        RuntimeError: If loading fails
        ValueError: If validation fails

    Example:
        >>> agent = load_agent("agentplug/analysis-agent", tools=["multiply", "add"])
        >>> result = agent.analyze_text("Calculate 5 * 3")
    """
    options = AgentLoadOptions(
        tools=tools,
        setup_environment=setup_environment,
        auto_install=auto_install,
        timeout=timeout,
        use_subprocess=use_subprocess,
    )

    loader = get_loader()
    result = loader.load(agent_name, options)

    if result.is_err():
        error = result.error
        if error.type == ErrorType.VALIDATION_ERROR:
            raise ValueError(error.message)
        else:
            raise RuntimeError(error.message)

    return result.unwrap()
