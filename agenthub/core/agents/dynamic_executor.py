"""Dynamic agent executor using reflection and manifest-based execution."""

import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DynamicExecutionError(Exception):
    """Raised when dynamic agent execution fails."""

    pass


class DynamicAgentExecutor:
    """Dynamic agent executor that uses reflection and manifest-based execution."""

    def __init__(self) -> None:
        """Initialize the dynamic executor."""
        self.loaded_agents: dict[str, type] = {}  # Cache for loaded agent classes

    def execute_agent_method(
        self,
        agent_path: str,
        method_name: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agent method dynamically using reflection.

        Args:
            agent_path: Path to the agent directory
            method_name: Name of the method to execute
            parameters: Dictionary of method parameters
            manifest: Optional manifest data for validation

        Returns:
            Dictionary with 'result' or 'error' key

        Raises:
            DynamicExecutionError: If execution fails
        """
        try:
            # Check if this is a Dana agent - dynamic execution only works for Python
            agent_config = self._get_agent_config(agent_path)
            if agent_config and "dana_version" in agent_config:
                raise DynamicExecutionError(
                    "Dynamic execution not supported for Dana agents. "
                    "Use subprocess execution instead."
                )

            # Clear cache to prevent state pollution between calls
            # This ensures each call gets a fresh agent class load
            agent_script = self._get_agent_script(agent_path)
            cache_key = str(agent_script)
            if cache_key in self.loaded_agents:
                del self.loaded_agents[cache_key]

            # Load agent class dynamically (fresh load)
            agent_class = self._load_agent_class(agent_path)

            # Create agent instance
            agent_instance = agent_class()

            # Get method dynamically
            if not hasattr(agent_instance, method_name):
                available_methods = self._get_available_methods(agent_instance)
                raise DynamicExecutionError(
                    f"Method '{method_name}' not found. "
                    f"Available methods: {available_methods}"
                )

            method = getattr(agent_instance, method_name)

            # Validate and map parameters dynamically
            mapped_parameters = self._map_parameters_dynamically(
                method, parameters, manifest, method_name
            )

            # Execute method
            result = method(**mapped_parameters)

            return {"result": result}

        except Exception as e:
            logger.error(f"Dynamic execution failed: {e}")
            return {"error": str(e)}

    def _get_agent_script(self, agent_path: str) -> Path:
        """
        Get the agent script path based on agent configuration.
        Supports both agent.py (Python) and agent.na (Dana).

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the agent script file
        """
        agent_dir = Path(agent_path)

        # Check agent configuration to determine script type
        agent_config = self._get_agent_config(agent_path)

        if agent_config and "dana_version" in agent_config:
            # Use Dana script
            agent_script = agent_dir / "agent.na"
            logger.info(f"Using Dana script for dynamic execution: {agent_path}")
        else:
            # Default to Python script
            agent_script = agent_dir / "agent.py"
            logger.info(f"Using Python script for dynamic execution: {agent_path}")

        return agent_script

    def _get_agent_config(self, agent_path: str) -> dict[str, Any] | None:
        """
        Get agent configuration from agent.yaml or agent.yml file.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Agent configuration dictionary or None if not found
        """
        agent_yaml_path = Path(agent_path) / "agent.yaml"
        agent_yml_path = Path(agent_path) / "agent.yml"

        config_path = None
        if agent_yaml_path.exists():
            config_path = agent_yaml_path
        elif agent_yml_path.exists():
            config_path = agent_yml_path

        if not config_path:
            return None

        try:
            import yaml

            with open(config_path) as f:
                return yaml.safe_load(f)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Failed to parse agent config: {e}")
            return None

    def _load_agent_class(self, agent_path: str) -> type:
        """
        Load agent class dynamically from agent script file.
        Supports both agent.py (Python) and agent.na (Dana).

        Args:
            agent_path: Path to the agent directory

        Returns:
            Agent class

        Raises:
            DynamicExecutionError: If loading fails
        """
        agent_script = self._get_agent_script(agent_path)

        if not agent_script.exists():
            raise DynamicExecutionError(f"Agent script not found: {agent_script}")

        # Use cache if available
        cache_key = str(agent_script)
        if cache_key in self.loaded_agents:
            return self.loaded_agents[cache_key]

        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("agent", agent_script)
            if spec is None or spec.loader is None:
                raise DynamicExecutionError(
                    f"Could not load agent module: {agent_script}"
                )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find agent class (look for classes that don't start with underscore)
            agent_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if not name.startswith("_") and obj.__module__ == module.__name__:
                    agent_class = obj
                    break

            if agent_class is None:
                raise DynamicExecutionError(f"No agent class found in {agent_script}")

            # Cache the class
            self.loaded_agents[cache_key] = agent_class
            return agent_class

        except Exception as e:
            raise DynamicExecutionError(f"Failed to load agent class: {e}") from e

    def _get_available_methods(self, agent_instance: Any) -> list[str]:
        """
        Get list of available methods from agent instance.

        Args:
            agent_instance: Agent instance

        Returns:
            List of method names
        """
        methods = []
        for name, _method in inspect.getmembers(agent_instance, inspect.ismethod):
            if not name.startswith("_"):
                methods.append(name)
        return methods

    def _map_parameters_dynamically(
        self,
        method: Any,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        method_name: str = "",
    ) -> dict[str, Any]:
        """
        Map parameters dynamically based on method signature and manifest.

        Args:
            method: Method to map parameters for
            parameters: Input parameters
            manifest: Optional manifest for validation
            method_name: Name of the method

        Returns:
            Mapped parameters dictionary
        """
        try:
            # Get method signature
            sig = inspect.signature(method)
            bound_args = {}

            # Get parameter definitions from manifest if available
            manifest_params = {}
            if manifest and method_name:
                manifest_params = self._get_manifest_parameters(manifest, method_name)

            # Map parameters based on signature
            for param_name, param_info in sig.parameters.items():
                if param_name in parameters:
                    # Direct parameter match
                    bound_args[param_name] = parameters[param_name]
                elif param_name in manifest_params:
                    # Try to get from manifest parameter mapping
                    manifest_param = manifest_params[param_name]
                    if (
                        manifest_param.get("required", False)
                        and param_name not in parameters
                    ):
                        # Try to find a suitable parameter value
                        mapped_value = self._find_suitable_parameter_value(
                            parameters, param_name, manifest_param
                        )
                        if mapped_value is not None:
                            bound_args[param_name] = mapped_value
                        else:
                            raise DynamicExecutionError(
                                f"Required parameter '{param_name}' not provided"
                            )
                    elif "default" in manifest_param:
                        bound_args[param_name] = manifest_param["default"]
                elif param_info.default != inspect.Parameter.empty:
                    # Use method signature default
                    bound_args[param_name] = param_info.default
                else:
                    # Try to find a suitable parameter value
                    mapped_value = self._find_suitable_parameter_value(
                        parameters, param_name, {}
                    )
                    if mapped_value is not None:
                        bound_args[param_name] = mapped_value
                    else:
                        raise DynamicExecutionError(
                            f"Required parameter '{param_name}' not provided"
                        )

            return bound_args

        except Exception as e:
            raise DynamicExecutionError(f"Parameter mapping failed: {e}") from e

    def _get_manifest_parameters(
        self, manifest: dict[str, Any], method_name: str
    ) -> dict[str, Any]:
        """Get parameter definitions from manifest for a specific method."""
        try:
            interface = manifest.get("interface", {})
            methods = interface.get("methods", {})
            method_def = methods.get(method_name, {})
            params = method_def.get("parameters", {})
            return params if isinstance(params, dict) else {}
        except Exception:
            return {}

    def _find_suitable_parameter_value(
        self,
        parameters: dict[str, Any],
        param_name: str,
        manifest_param: dict[str, Any],
    ) -> Any:
        """
        Find a suitable parameter value using intelligent mapping.

        Args:
            parameters: Available parameters
            param_name: Target parameter name
            manifest_param: Manifest parameter definition

        Returns:
            Suitable parameter value or None
        """
        # If there's only one parameter and it's not named, use it
        if len(parameters) == 1:
            single_key = list(parameters.keys())[0]
            if single_key in ["input", "data", "value", "param"]:
                return parameters[single_key]

        # Try exact name match
        if param_name in parameters:
            return parameters[param_name]

        # Try case-insensitive match
        for key, value in parameters.items():
            if key.lower() == param_name.lower():
                return value

        # Try partial name match
        for key, value in parameters.items():
            if param_name.lower() in key.lower() or key.lower() in param_name.lower():
                return value

        # If no match found, return None
        return None


def execute_agent_dynamically(
    agent_path: str,
    method_name: str,
    parameters: dict[str, Any],
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convenience function for dynamic agent execution.

    Args:
        agent_path: Path to the agent directory
        method_name: Name of the method to execute
        parameters: Dictionary of method parameters
        manifest: Optional manifest data for validation

    Returns:
        Dictionary with 'result' or 'error' key
    """
    executor = DynamicAgentExecutor()
    return executor.execute_agent_method(agent_path, method_name, parameters, manifest)
