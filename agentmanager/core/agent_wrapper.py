"""Agent wrapper for unified agent interface."""

import logging

from agentmanager.core.interface_validator import InterfaceValidator

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""

    pass


class AgentWrapper:
    """Unified wrapper for agent operations."""

    def __init__(self, agent_info: dict, runtime=None):
        """
        Initialize the agent wrapper.

        Args:
            agent_info: Agent information from AgentLoader
            runtime: Optional runtime for executing methods
        """
        self.agent_info = agent_info
        self.runtime = runtime
        self.interface_validator = InterfaceValidator()

        # Extract key information for easy access
        self.name = agent_info.get("name", "unknown")
        self.namespace = agent_info.get("namespace", "unknown")
        self.agent_name = agent_info.get("agent_name", "unknown")
        self.path = agent_info.get("path", "")
        self.version = agent_info.get("version", "unknown")
        self.description = agent_info.get("description", "")
        self.methods = agent_info.get("methods", [])
        self.dependencies = agent_info.get("dependencies", [])

        # Extract interface for method operations
        self.manifest = agent_info.get("manifest", {})
        self.interface = self.manifest.get("interface", {})

    def has_method(self, method_name: str) -> bool:
        """
        Check if the agent has a specific method.

        Args:
            method_name: Name of the method to check

        Returns:
            True if method exists
        """
        return method_name in self.methods

    def get_method_info(self, method_name: str) -> dict:
        """
        Get information about a specific method.

        Args:
            method_name: Name of the method

        Returns:
            Method information dictionary

        Raises:
            AgentExecutionError: If method doesn't exist
        """
        if not self.has_method(method_name):
            available = ", ".join(self.methods) if self.methods else "none"
            raise AgentExecutionError(
                f"Method '{method_name}' not available in agent '{self.name}'. "
                f"Available methods: {available}"
            )

        return self.interface_validator.get_method_info(self.interface, method_name)

    def execute(self, method_name: str, parameters: dict) -> dict:
        """
        Execute an agent method.

        Args:
            method_name: Name of the method to execute
            parameters: Method parameters

        Returns:
            Execution result

        Raises:
            AgentExecutionError: If execution fails
        """
        if not self.runtime:
            raise AgentExecutionError("No runtime provided for agent execution")

        if not self.has_method(method_name):
            available = ", ".join(self.methods) if self.methods else "none"
            raise AgentExecutionError(
                f"Method '{method_name}' not available in agent '{self.name}'. "
                f"Available methods: {available}"
            )

        try:
            result = self.runtime.execute_agent(
                self.namespace, self.agent_name, method_name, parameters
            )
            return result
        except Exception as e:
            raise AgentExecutionError(f"Failed to execute {method_name}: {e}") from e

    def __getattr__(self, method_name: str):
        """
        Magic method to enable direct method calls on the wrapper.

        Args:
            method_name: Name of the method being called

        Returns:
            Callable that executes the agent method

        Raises:
            AttributeError: If method doesn't exist
        """
        if method_name.startswith("_") or not self.has_method(method_name):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{method_name}'"
            )

        def method_caller(**kwargs):
            """Execute the agent method with provided arguments."""
            return self.execute(method_name, kwargs)

        return method_caller

    def __repr__(self) -> str:
        """String representation of the agent wrapper."""
        return (
            f"AgentWrapper(name='{self.namespace}/{self.agent_name}', "
            f"methods={self.methods}, version='{self.version}')"
        )

    def to_dict(self) -> dict:
        """
        Convert agent wrapper to dictionary representation.

        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.name,
            "namespace": self.namespace,
            "agent_name": self.agent_name,
            "version": self.version,
            "description": self.description,
            "path": self.path,
            "methods": self.methods,
            "dependencies": self.dependencies,
            "has_runtime": self.runtime is not None,
        }
