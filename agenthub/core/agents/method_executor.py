"""Method execution and parameter mapping."""

import json
import logging
import os
import warnings
from typing import Any

from ..tools.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

# Parameter types (agent.yaml interface.methods.<m>.parameters.<p>.type)
# whose string values get file-path resolution before reaching the agent.
_FILE_PATH_TYPES = frozenset({"file", "path", "file_path", "filepath"})


class MethodExecutor:
    """Handles method execution and parameter mapping."""

    def __init__(self, agent_wrapper: Any) -> None:
        """Initialize method executor."""
        self.agent_wrapper = agent_wrapper

    def execute(self, method: str, parameters: dict[str, Any]) -> Any:
        """
        Execute an agent method with parameters.

        Args:
            method: Name of the method to execute
            parameters: Dictionary of parameters to pass to the method

        Returns:
            Result of the method execution

        Raises:
            AgentExecutionError: If execution fails
        """
        if not self.agent_wrapper.agent_info.has_method(method):
            available_methods = ", ".join(self.agent_wrapper.agent_info.methods)
            raise AgentExecutionError(
                f"Method '{method}' not found in agent '{self.agent_wrapper.name}'! "
                f"Available methods: {available_methods}"
            )

        try:
            # Map parameters if needed
            mapped_params = self._map_parameters(method, parameters)

            # Prepare tool context (the wrapper builds the dict once; the
            # runtime serializes it for transport)
            tool_context = self.agent_wrapper.get_tool_context()

            # Resolve file paths in parameters (schema-aware)
            resolved_params = self._resolve_file_paths(method, mapped_params)

            # Generate agent call JSON (for future use if needed)
            # agent_call_json = self.generate_agent_call_json(method, resolved_params)

            # Execute through runtime
            if self.agent_wrapper.runtime:
                result = self.agent_wrapper.runtime.execute_agent(
                    namespace=self.agent_wrapper.namespace,
                    agent_name=self.agent_wrapper.name,
                    method=method,
                    parameters=resolved_params,
                    tool_context=tool_context,
                )
                return result
            else:
                # Fallback execution
                logger.warning("No runtime available, using fallback execution")
                return {
                    "result": f"Method '{method}' executed with parameters: "
                    f"{resolved_params}"
                }

        except Exception as e:
            logger.error(f"Error executing method '{method}': {e}")
            raise AgentExecutionError(
                f"Failed to execute method '{method}': {e}"
            ) from e

    def _map_parameters(
        self, method: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Map parameters to the correct format for the method."""
        # Check if parameters contain positional args that need mapping
        if "args" in parameters and parameters["args"]:
            args = parameters["args"]
            kwargs = {k: v for k, v in parameters.items() if k != "args"}

            # Get method info for parameter mapping
            method_info = self.agent_wrapper.agent_info.get_method_info(method)
            interface_params = method_info.get("parameters", {})

            if not kwargs and interface_params:
                # Map positional args to named parameters
                mapped_kwargs = self._map_positional_to_named_args(method, args, {})
                return mapped_kwargs
            elif args and kwargs and interface_params:
                # Handle mixed positional and named arguments
                mapped_kwargs = self._map_mixed_arguments(method, args, kwargs)
                return mapped_kwargs
            else:
                # No declared interface: positional args pass through as a
                # literal "args" tuple, which agent methods almost never
                # accept. One release with a warning, then a typed error.
                warnings.warn(
                    f"Positional arguments passed to method '{method}', which "
                    f"declares no interface parameters; the runtime receives "
                    f"them as a raw 'args' tuple. Pass keyword arguments or "
                    f"declare parameters in agent.yaml — this becomes an "
                    f"AgentExecutionError in the next minor release.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                return parameters
        else:
            # No positional args, return as-is
            return parameters

    def _map_positional_to_named_args(
        self, method_name: str, args: list[Any], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Map positional arguments to named parameters based on method signature."""
        method_info = self.agent_wrapper.agent_info.get_method_info(method_name)
        parameters = method_info.get("parameters", {})

        # Get parameter names in order
        param_names = list(parameters.keys())
        mapped_params = kwargs.copy()

        # Map positional args to named parameters
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_name = param_names[i]
                if param_name not in mapped_params:
                    mapped_params[param_name] = arg

        return mapped_params

    def _map_mixed_arguments(
        self, method_name: str, args: list[Any], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle mixed positional and keyword arguments."""
        method_info = self.agent_wrapper.agent_info.get_method_info(method_name)
        parameters = method_info.get("parameters", {})

        # Map positional args first
        mapped_params = self._map_positional_to_named_args(method_name, args, {})

        # Add keyword arguments
        mapped_params.update(kwargs)

        # Validate required parameters
        self._validate_required_parameters(method_name, mapped_params, parameters)

        return mapped_params

    def _validate_required_parameters(
        self,
        method_name: str,
        parameters: dict[str, Any],
        method_schema: dict[str, Any],
    ) -> None:
        """Validate that all required parameters are provided."""
        missing_params = []

        for param_name, param_info in method_schema.items():
            if param_info.get("required", False) and param_name not in parameters:
                missing_params.append(param_name)

        if missing_params:
            raise AgentExecutionError(
                f"Missing required parameters for method '{method_name}': "
                f"{missing_params}"
            )

    def _resolve_file_paths(
        self, method: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve file paths in parameters to absolute paths.

        Schema-aware: parameters whose manifest declaration has a file-path
        type (``file``, ``path``, ``file_path``, ``filepath``) are resolved;
        parameters with any other declared type pass through untouched.
        Undeclared parameters fall back to the legacy string heuristic for
        one release, with a DeprecationWarning when it classifies a value.
        """
        method_info = self.agent_wrapper.agent_info.get_method_info(method)
        schema = method_info.get("parameters", {})
        resolved_params = {}

        for key, value in parameters.items():
            declared = schema.get(key)
            declared_type = declared.get("type") if isinstance(declared, dict) else None

            if not isinstance(value, str):
                resolved_params[key] = value
            elif declared_type in _FILE_PATH_TYPES:
                resolved_params[key] = self._resolve_single_path(value)
            elif declared_type is not None:
                # Declared as a non-file type: never rewrite the value
                resolved_params[key] = value
            elif self._looks_like_file_path(value):
                # Undeclared parameter: legacy heuristic, one more release
                warnings.warn(
                    f"Parameter '{key}' of method '{method}' has no declared "
                    f"type and was treated as a file path by the legacy "
                    f"heuristic; declare 'type: file' (to keep resolution) "
                    f"or any other type (to opt out) in agent.yaml. The "
                    f"heuristic is removed in the next minor release.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                resolved_params[key] = self._resolve_single_path(value)
            else:
                resolved_params[key] = value

        return resolved_params

    def _resolve_single_path(self, value: str) -> str:
        """Resolve one path-like string against the agent dir, then cwd."""
        if not os.path.isabs(value):
            # Try relative to agent path
            agent_path = self.agent_wrapper.agent_info.path
            if agent_path:
                resolved_path = os.path.join(agent_path, value)
                if os.path.exists(resolved_path):
                    return os.path.abspath(resolved_path)

            # Try relative to current working directory
            if os.path.exists(value):
                return os.path.abspath(value)

        # Keep original if can't resolve
        return value

    def _looks_like_file_path(self, value: str) -> bool:
        """Check if a string looks like a file path."""
        # Simple heuristic: contains path separators or has file extension
        return "/" in value or "\\" in value or (len(value) > 4 and "." in value[-5:])

    def generate_agent_call_json(self, method: str, parameters: dict[str, Any]) -> str:
        """Generate JSON for agent method calls."""
        call_data = {
            "method": method,
            "parameters": parameters,
            "agent_id": self.agent_wrapper.agent_id,
            "timestamp": json.dumps({"timestamp": "now"}),
        }

        return json.dumps(call_data, indent=2)

    def get_execution_context(self) -> dict[str, Any]:
        """Get execution context for the agent."""
        return {
            "agent_id": self.agent_wrapper.agent_id,
            "agent_name": self.agent_wrapper.agent_info.name,
            "available_methods": self.agent_wrapper.agent_info.methods,
            "has_runtime": self.agent_wrapper.runtime is not None,
            "tool_context": self.agent_wrapper.get_tool_context_json(),
        }
