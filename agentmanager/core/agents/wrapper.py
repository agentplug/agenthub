"""Agent wrapper for unified agent interface."""

import logging

from .validator import InterfaceValidator

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
        if method_name.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{method_name}'"
            )

        if not self.has_method(method_name):
            # Provide helpful error message with available methods
            available_methods = ", ".join(self.methods) if self.methods else "none"

            # Try to find similar method names
            similar_methods = []
            if self.methods:
                method_name_lower = method_name.lower()
                for method in self.methods:
                    if (
                        method_name_lower in method.lower()
                        or method.lower() in method_name_lower
                    ):
                        similar_methods.append(method)

            error_msg = (
                f"Method '{method_name}' not found in agent '{self.name}'!\n"
                f"📋 Available methods: {available_methods}"
            )

            if similar_methods:
                error_msg += (
                    f"\n💡 Did you mean one of these? {', '.join(similar_methods)}"
                )

            # Show method details for better guidance
            if self.methods:
                error_msg += "\n\n🔍 Method details:"
                for method in self.methods:
                    try:
                        method_info = self.get_method_info(method)
                        description = method_info.get("description", "No description")
                        error_msg += f"\n   • {method}: {description}"
                    except Exception:
                        error_msg += f"\n   • {method}: Available"

            raise AttributeError(error_msg)

        def method_caller(*args, **kwargs):
            """Execute the agent method with provided arguments."""
            # Get method information from the agent's interface
            try:
                method_info = self.get_method_info(method_name)
                interface_params = method_info.get("parameters", {})

                # If no kwargs provided, try to map positional args to parameters
                if args and not kwargs:
                    kwargs = self._map_positional_to_named_args(
                        method_name, args, interface_params
                    )
                elif args and kwargs:
                    # Handle mixed positional and named arguments
                    kwargs = self._map_mixed_arguments(
                        method_name, args, kwargs, interface_params
                    )

                # Validate required parameters
                self._validate_required_parameters(
                    method_name, kwargs, interface_params
                )

                return self.execute(method_name, kwargs)

            except Exception as e:
                # Provide helpful error message for debugging
                available_params = (
                    list(interface_params.keys()) if interface_params else []
                )
                raise AgentExecutionError(
                    f"Failed to prepare parameters for {method_name}. "
                    f"Available parameters: {available_params}. "
                    f"Error: {e}"
                ) from e

        return method_caller

    def _map_positional_to_named_args(
        self, method_name: str, args: tuple, interface_params: dict
    ) -> dict:
        """
        Map positional arguments to named parameters based on the agent's interface.

        Args:
            method_name: Name of the method being called
            args: Positional arguments provided by user
            interface_params: Parameter definitions from agent interface

        Returns:
            Dictionary mapping parameter names to values
        """
        if not interface_params:
            # No parameters defined, return empty dict
            return {}

        param_names = list(interface_params.keys())
        kwargs = {}

        # Map positional args to parameter names
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_name = param_names[i]
                kwargs[param_name] = arg
            else:
                # Too many positional arguments
                raise AgentExecutionError(
                    f"Method '{method_name}' expects at most {len(param_names)} "
                    f"positional arguments, but {len(args)} were provided. "
                    f"Available parameters: {param_names}"
                )

        return kwargs

    def _map_mixed_arguments(
        self, method_name: str, args: tuple, kwargs: dict, interface_params: dict
    ) -> dict:
        """
        Map mixed positional and named arguments to the final parameter dictionary.

        Args:
            method_name: Name of the method being called
            args: Positional arguments provided by user
            kwargs: Named arguments provided by user
            interface_params: Parameter definitions from agent interface

        Returns:
            Dictionary mapping parameter names to values
        """
        if not interface_params:
            return kwargs

        param_names = list(interface_params.keys())
        final_kwargs = kwargs.copy()  # Start with existing named arguments

        # Map positional args to parameters that aren't already specified in kwargs
        pos_arg_index = 0
        for param_name in param_names:
            if param_name not in final_kwargs and pos_arg_index < len(args):
                final_kwargs[param_name] = args[pos_arg_index]
                pos_arg_index += 1

        # Check if we have too many positional arguments
        if pos_arg_index < len(args):
            raise AgentExecutionError(
                f"Method '{method_name}' received {len(args)} positional arguments "
                f"but only {pos_arg_index} could be mapped to parameters. "
                f"Available parameters: {param_names}"
            )

        return final_kwargs

    def _validate_required_parameters(
        self, method_name: str, kwargs: dict, interface_params: dict
    ):
        """
        Validate that all required parameters are provided.

        Args:
            method_name: Name of the method being called
            kwargs: Parameters provided by user
            interface_params: Parameter definitions from agent interface
        """
        if not interface_params:
            return

        for param_name, param_info in interface_params.items():
            # Check if parameter is required (not marked as optional)
            # A parameter is optional if it has a default value or is explicitly
            # marked as optional
            has_default = "default" in param_info
            is_optional = param_info.get("optional", False) or has_default

            if not is_optional and param_name not in kwargs:
                raise AgentExecutionError(
                    f"Method '{method_name}' requires parameter '{param_name}' "
                    f"but it was not provided. "
                    f"Available parameters: {list(interface_params.keys())}"
                )

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
