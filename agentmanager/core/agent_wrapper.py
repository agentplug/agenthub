"""Agent wrapper for unified agent interface."""

import logging
from typing import Dict, Any, List, Optional

from agentmanager.core.interface_validator import InterfaceValidator
from agentmanager.core.custom_method_manager import CustomMethodManager
from agentmanager.core.exceptions import MethodNotFoundError, MethodInjectionError

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""

    pass


class AgentWrapper:
    """Unified wrapper for agent operations."""

    def __init__(self, agent_info: dict, runtime=None, custom_method_manager: CustomMethodManager = None):
        """
        Initialize the agent wrapper.

        Args:
            agent_info: Agent information from AgentLoader
            runtime: Optional runtime for executing methods
            custom_method_manager: Optional custom method manager for method injection
        """
        self.agent_info = agent_info
        self.runtime = runtime
        self.custom_method_manager = custom_method_manager or CustomMethodManager()
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
        
        # Load custom methods
        self._load_custom_methods()

    def _load_custom_methods(self):
        """Load custom methods for this agent."""
        try:
            agent_path = f"{self.namespace}/{self.agent_name}"
            custom_methods = self.custom_method_manager.list_methods(agent_path)
            self.custom_methods = list(custom_methods.keys())
            logger.debug(f"Loaded {len(self.custom_methods)} custom methods for agent {agent_path}")
        except Exception as e:
            logger.warning(f"Failed to load custom methods: {e}")
            self.custom_methods = []

    def has_method(self, method_name: str) -> bool:
        """
        Check if the agent has a specific method (built-in or custom).

        Args:
            method_name: Name of the method to check

        Returns:
            True if method exists
        """
        return method_name in self.methods or method_name in self.custom_methods

    def is_custom_method(self, method_name: str) -> bool:
        """
        Check if a method is a custom injected method.

        Args:
            method_name: Name of the method to check

        Returns:
            True if method is custom
        """
        return method_name in self.custom_methods

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
            available = ", ".join(self.methods + self.custom_methods) if (self.methods or self.custom_methods) else "none"
            raise AgentExecutionError(
                f"Method '{method_name}' not available in agent '{self.name}'. "
                f"Available methods: {available}"
            )

        # Check if it's a custom method
        if self.is_custom_method(method_name):
            try:
                agent_path = f"{self.namespace}/{self.agent_name}"
                method_info = self.custom_method_manager.get_method_info(agent_path, method_name)
                if method_info:
                    return {
                        "name": method_info.name,
                        "description": f"Custom {method_info.language} method",
                        "language": method_info.language,
                        "injected_at": method_info.injected_at,
                        "security_score": getattr(method_info, 'security_score', 'unknown'),
                        "custom": True
                    }
            except Exception as e:
                logger.warning(f"Failed to get custom method info for {method_name}: {e}")

        # Return built-in method info
        return self.interface_validator.get_method_info(self.interface, method_name)

    def execute(self, method_name: str, parameters: dict) -> dict:
        """
        Execute an agent method (built-in or custom).

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
            available = ", ".join(self.methods + self.custom_methods) if (self.methods or self.custom_methods) else "none"
            raise AgentExecutionError(
                f"Method '{method_name}' not available in agent '{self.name}'. "
                f"Available methods: {available}"
            )

        try:
            # Execute using runtime
            result = self.runtime.execute_agent(
                self.namespace, self.agent_name, method_name, parameters
            )
            return result
        except Exception as e:
            raise AgentExecutionError(f"Failed to execute {method_name}: {e}") from e

    def inject_custom_method(self, method_name: str, implementation: Any, language: str = "python") -> dict:
        """
        Inject a custom method for this agent.

        Args:
            method_name: Name of the method to inject
            implementation: Method implementation
            language: Programming language of the implementation

        Returns:
            Injection result dictionary

        Raises:
            MethodInjectionError: If injection fails
        """
        try:
            agent_path = f"{self.namespace}/{self.agent_name}"
            self.custom_method_manager.inject_method(agent_path, method_name, implementation, language)
            
            # Reload custom methods
            self._load_custom_methods()
            
            logger.info(f"Successfully injected custom method '{method_name}' for agent '{self.name}'")
            
            return {
                "success": True,
                "message": f"Successfully injected custom method '{method_name}' for agent '{self.name}'",
                "method_name": method_name,
                "language": language,
                "agent_path": agent_path
            }
            
        except Exception as e:
            logger.error(f"Failed to inject custom method '{method_name}': {e}")
            raise MethodInjectionError(
                f"Failed to inject custom method: {str(e)}",
                agent_path=f"{self.namespace}/{self.agent_name}",
                method_name=method_name,
                cause=e
            )

    def remove_custom_method(self, method_name: str) -> dict:
        """
        Remove a custom method from this agent.

        Args:
            method_name: Name of the method to remove

        Returns:
            Removal result dictionary

        Raises:
            MethodNotFoundError: If method doesn't exist
        """
        if not self.is_custom_method(method_name):
            raise MethodNotFoundError(
                f"Method '{method_name}' is not a custom method",
                agent_path=f"{self.namespace}/{self.agent_name}",
                method_name=method_name
            )

        try:
            agent_path = f"{self.namespace}/{self.agent_name}"
            self.custom_method_manager.remove_method(agent_path, method_name)
            
            # Reload custom methods
            self._load_custom_methods()
            
            logger.info(f"Successfully removed custom method '{method_name}' from agent '{self.name}'")
            
            return {
                "success": True,
                "message": f"Successfully removed custom method '{method_name}' from agent '{self.name}'",
                "method_name": method_name,
                "agent_path": agent_path
            }
            
        except Exception as e:
            logger.error(f"Failed to remove custom method '{method_name}': {e}")
            raise MethodInjectionError(
                f"Failed to remove custom method: {str(e)}",
                agent_path=f"{self.namespace}/{self.agent_name}",
                method_name=method_name,
                cause=e
            )

    def list_custom_methods(self) -> List[Dict[str, Any]]:
        """
        List all custom methods for this agent.

        Returns:
            List of custom method information dictionaries
        """
        try:
            agent_path = f"{self.namespace}/{self.agent_name}"
            custom_methods = self.custom_method_manager.list_methods(agent_path)
            
            method_list = []
            for method_name, method_info in custom_methods.items():
                method_list.append({
                    "name": method_name,
                    "language": method_info.language,
                    "injected_at": method_info.injected_at,
                    "security_score": getattr(method_info, 'security_score', 'unknown'),
                    "metadata": method_info.metadata
                })
            
            return method_list
            
        except Exception as e:
            logger.warning(f"Failed to list custom methods: {e}")
            return []

    def get_custom_method_context(self) -> dict:
        """
        Get execution context for custom methods.

        Returns:
            Dictionary with custom method context information
        """
        try:
            agent_path = f"{self.namespace}/{self.agent_name}"
            return self.custom_method_manager.get_method_context(agent_path)
        except Exception as e:
            logger.warning(f"Failed to get custom method context: {e}")
            return {}

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
            all_methods = self.methods + self.custom_methods
            available_methods = ", ".join(all_methods) if all_methods else "none"

            # Try to find similar method names
            similar_methods = []
            if all_methods:
                method_name_lower = method_name.lower()
                for method in all_methods:
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
            if all_methods:
                error_msg += "\n\n🔍 Method details:"
                for method in all_methods:
                    try:
                        method_info = self.get_method_info(method)
                        description = method_info.get("description", "No description")
                        method_type = "🔧 Custom" if self.is_custom_method(method) else "📦 Built-in"
                        error_msg += f"\n   • {method}: {description} ({method_type})"
                    except Exception:
                        method_type = "🔧 Custom" if self.is_custom_method(method) else "📦 Built-in"
                        error_msg += f"\n   • {method}: Available ({method_type})"

            raise AttributeError(error_msg)

        def method_caller(*args, **kwargs):
            """Execute the agent method with provided arguments."""
            # Get method information from the agent's interface or custom method
            try:
                method_info = self.get_method_info(method_name)
                interface_params = method_info.get("parameters", {})
                
                # For custom methods, we might not have detailed parameter info
                if self.is_custom_method(method_name):
                    # Use parameters as-is for custom methods
                    return self.execute(method_name, kwargs if kwargs else dict(zip(range(len(args)), args)))

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
        custom_count = len(self.custom_methods)
        total_count = len(self.methods) + custom_count
        return (
            f"AgentWrapper(name='{self.namespace}/{self.agent_name}', "
            f"methods={total_count} (built-in: {len(self.methods)}, custom: {custom_count}), "
            f"version='{self.version}')"
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
            "custom_methods": self.custom_methods,
            "dependencies": self.dependencies,
            "has_runtime": self.runtime is not None,
            "total_methods": len(self.methods) + len(self.custom_methods)
        }
