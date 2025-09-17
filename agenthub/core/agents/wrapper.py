"""Agent wrapper for unified agent interface with tool capabilities."""

import json
import logging
from typing import Any

from .validator import InterfaceValidator

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""

    pass


class AgentWrapper:
    """Unified wrapper for agent operations."""

    def __init__(
        self,
        agent_info: dict,
        tool_registry=None,
        agent_id: str = None,
        assigned_tools: list[str] = None,
        runtime=None,
    ):
        """
        Initialize the agent wrapper with tool capabilities.

        Args:
            agent_info: Agent information from AgentLoader
            tool_registry: Optional tool registry for tool capabilities
            agent_id: Unique identifier for this agent
            assigned_tools: List of tools assigned to this agent
            runtime: Optional runtime for executing methods
        """
        self.agent_info = agent_info
        self.tool_registry = tool_registry
        self.agent_id = (
            agent_id
            or f"{agent_info.get('namespace', 'unknown')}/"
            f"{agent_info.get('name', 'unknown')}"
        )
        self.assigned_tools = assigned_tools or []
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

    def assign_tools(self, tool_names: list[str]) -> None:
        """
        Assign tools to this agent.

        Args:
            tool_names: List of tool names to assign to this agent
        """
        if self.tool_registry:
            self.tool_registry.assign_tools_to_agent(self.agent_id, tool_names)
            self.assigned_tools = tool_names.copy()
        else:
            raise RuntimeError("No tool registry available for tool assignment")

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
            # Pass tool context if tools are assigned
            tool_context = None
            if self.assigned_tools and self.tool_registry:
                tool_context_json = self.get_tool_context_json()
                tool_context = json.loads(tool_context_json)

            result = self.runtime.execute_agent(
                self.namespace, self.agent_name, method_name, parameters, tool_context
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
            "assigned_tools": self.assigned_tools,
        }

    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Execute a tool with access control.

        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            Tool execution result

        Raises:
            PermissionError: If agent doesn't have access to the tool
            ValueError: If tool doesn't exist
        """
        if not self.tool_registry:
            raise ValueError("No tool registry available")

        # Check if agent has access to this tool
        from ..tools import can_agent_access_tool, get_tool_function

        if not can_agent_access_tool(self.agent_id, tool_name):
            raise PermissionError(
                f"Agent '{self.agent_id}' does not have access to tool '{tool_name}'"
            )

        # Get tool function
        tool_func = get_tool_function(tool_name)
        if not tool_func:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Execute tool
        try:
            result = tool_func(*args, **kwargs)
            print(f"🔧 Agent '{self.agent_id}' executed tool '{tool_name}': {result}")
            return result
        except Exception as e:
            print(f"❌ Agent '{self.agent_id}' error executing tool '{tool_name}': {e}")
            raise

    def can_access_tool(self, tool_name: str) -> bool:
        """Check if agent can access a specific tool."""
        if not self.tool_registry:
            return False

        return self.tool_registry.can_agent_access_tool(self.agent_id, tool_name)

    def get_available_tools(self) -> list[str]:
        """Get list of tools available to this agent."""
        return self.assigned_tools

    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has access to a specific tool."""
        return self.can_access_tool(tool_name)

    def search_tools(self, query: str) -> list[str]:
        """Search tools by name or description."""
        if not query:
            return self.assigned_tools

        matching_tools = []
        for tool_name in self.assigned_tools:
            if query.lower() in tool_name.lower():
                matching_tools.append(tool_name)
            else:
                # Check tool description
                try:
                    metadata = self.get_tool_metadata(tool_name)
                    if (
                        metadata
                        and query.lower() in metadata.get("description", "").lower()
                    ):
                        matching_tools.append(tool_name)
                except Exception:
                    pass

        return matching_tools

    def get_tool_help(self, tool_name: str) -> str:
        """Get help information for a tool."""
        if not self.has_tool(tool_name):
            return f"Tool '{tool_name}' not available to this agent"

        try:
            metadata = self.get_tool_metadata(tool_name)
            if not metadata:
                return f"Tool '{tool_name}' - No metadata available"

            help_text = f"Tool: {tool_name}\n"
            help_text += (
                f"Description: {metadata.get('description', 'No description')}\n"
            )

            parameters = metadata.get("parameters", {})
            if parameters:
                help_text += "Parameters:\n"
                for param_name, param_info in parameters.items():
                    param_type = param_info.get("type", "unknown")
                    required = param_info.get("required", False)
                    help_text += (
                        f"  {param_name} ({param_type}){'*' if required else ''}\n"
                    )

            return help_text
        except Exception as e:
            return f"Tool '{tool_name}' - Error getting help: {e}"

    def get_tool_metadata(self, tool_name: str) -> dict[str, Any] | None:
        """Get metadata for a tool (only if agent has access)."""
        if not self.can_access_tool(tool_name) or not self.tool_registry:
            return None

        metadata = self.tool_registry.get_tool_metadata(tool_name)
        if metadata:
            return {
                "name": metadata.name,
                "description": metadata.description,
                "namespace": metadata.namespace,
                "parameters": metadata.parameters,
                "examples": metadata.examples,
            }
        return None

    def get_assigned_tools(self) -> list[str]:
        """Get list of tools assigned to this agent."""
        return self.assigned_tools.copy()

    def get_tool_instructions(self) -> str:
        """
        Generate tool usage instructions for the agent.

        Returns:
            Formatted string with tool usage instructions
        """
        if not self.assigned_tools or not self.tool_registry:
            return ""

        instructions = []
        instructions.append("🔧 AVAILABLE TOOLS:")
        instructions.append(
            "You have access to the following tools. Use them when appropriate:"
        )
        instructions.append("")

        for tool_name in self.assigned_tools:
            metadata = self.get_tool_metadata(tool_name)
            if metadata:
                instructions.append(f"• {tool_name}: {metadata['description']}")

                # Add usage examples from metadata
                if metadata.get("examples"):
                    for example in metadata["examples"]:
                        # Convert from function call format to execute_tool format
                        if "(" in example:
                            # Extract parameters from example like
                            # "add('param1', 'param2')"
                            func_name = example.split("(")[0]
                            params_part = example.split("(", 1)[1].rsplit(")", 1)[0]
                            if params_part.strip():
                                instructions.append(
                                    f"  Usage: execute_tool('{func_name}', "
                                    f"{params_part})"
                                )
                            else:
                                instructions.append(
                                    f"  Usage: execute_tool('{func_name}')"
                                )
                        else:
                            instructions.append(f"  Usage: execute_tool('{tool_name}')")
                        break  # Only show first example

                instructions.append("")

        instructions.append("💡 TOOL USAGE GUIDELINES:")
        instructions.append("- Use tools when they can help solve the user's request")
        instructions.append("- Call execute_tool(tool_name, *args) to use a tool")
        instructions.append("- Tools return results that you can use in your response")
        instructions.append("- If a tool fails, explain the error to the user")
        instructions.append("")

        return "\n".join(instructions)

    def inject_tool_context(self) -> None:
        """
        Inject tool context into the agent's environment.
        This method should be called to make tools available to the agent.
        """
        if not self.assigned_tools or not self.tool_registry:
            return

        # Add tool execution method to agent's context
        if hasattr(self, "execute_tool"):
            # Make execute_tool available in the agent's namespace
            if hasattr(self, "agent_info") and "manifest" in self.agent_info:
                # This would be where we inject the tool context
                # For now, we'll just store the instructions
                self._tool_instructions = self.get_tool_instructions()
                print(f"🔧 Injected tool context for agent '{self.agent_id}'")
                print(f"📋 Available tools: {self.assigned_tools}")

    def get_tool_context(self) -> dict[str, Any]:
        """
        Get tool context information for the agent.

        Returns:
            Dictionary with tool context information
        """
        if not self.assigned_tools or not self.tool_registry:
            return {}

        return {
            "assigned_tools": self.assigned_tools,
            "tool_instructions": self.get_tool_instructions(),
            "execute_tool_method": self.execute_tool,
            "can_access_tool_method": self.can_access_tool,
            "get_tool_metadata_method": self.get_tool_metadata,
        }

    def get_tool_context_json(self) -> str:
        """
        Get tool context in JSON format compatible with agent execution.

        Returns:
            JSON string with tool context in the format expected by agents
        """
        if not self.assigned_tools or not self.tool_registry:
            return json.dumps(
                {
                    "available_tools": [],
                    "tool_descriptions": {},
                    "tool_usage_examples": {},
                    "tool_parameters": {},
                    "tool_return_types": {},
                    "tool_namespaces": {},
                }
            )

        # Get tool descriptions and usage examples
        tool_descriptions = {}
        tool_usage_examples = {}
        tool_parameters = {}
        tool_return_types = {}
        tool_namespaces = {}

        for tool_name in self.assigned_tools:
            metadata = self.get_tool_metadata(tool_name)
            if metadata:
                tool_descriptions[tool_name] = metadata["description"]

                # Use dynamically generated examples from ToolMetadata
                if metadata.get("examples"):
                    tool_usage_examples[tool_name] = metadata["examples"]
                else:
                    # Fallback to basic example if no examples available
                    tool_usage_examples[tool_name] = [f"{tool_name}()"]

                # Add parameters and return types (convert types to strings for
                # JSON serialization)
                params = metadata.get("parameters", {})
                serialized_params = {}
                for param_name, param_info in params.items():
                    if isinstance(param_info, dict):
                        serialized_param = param_info.copy()
                        if "type" in serialized_param and hasattr(
                            serialized_param["type"], "__name__"
                        ):
                            serialized_param["type"] = serialized_param["type"].__name__
                        serialized_params[param_name] = serialized_param
                    else:
                        serialized_params[param_name] = param_info

                tool_parameters[tool_name] = serialized_params

                return_type = metadata.get("return_type", "unknown")
                if hasattr(return_type, "__name__"):
                    return_type = return_type.__name__
                tool_return_types[tool_name] = return_type
                tool_namespaces[tool_name] = metadata.get("namespace", "custom")

        return json.dumps(
            {
                "available_tools": self.assigned_tools,
                "tool_descriptions": tool_descriptions,
                "tool_usage_examples": tool_usage_examples,
                "tool_parameters": tool_parameters,
                "tool_return_types": tool_return_types,
                "tool_namespaces": tool_namespaces,
            }
        )

    def generate_agent_call_json(self, method: str, parameters: dict[str, Any]) -> str:
        """
        Generate a complete agent call JSON with tool context.

        Args:
            method: Agent method to call
            parameters: Parameters for the method

        Returns:
            JSON string ready for agent execution
        """

        tool_context_json = self.get_tool_context_json()
        tool_context = json.loads(tool_context_json)

        call_data = {
            "method": method,
            "parameters": parameters,
            "tool_context": tool_context,
        }

        return json.dumps(call_data, indent=2)
