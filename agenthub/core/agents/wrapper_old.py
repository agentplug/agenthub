"""Enhanced agent wrapper for Phase 3 with tool management and knowledge injection."""

import json
import logging
import os
import time
from typing import Any

from ..knowledge import KnowledgeManager
from ..llm.llm_decision_maker import LLMDecisionMaker
from ..mcp.agent_tool_manager import AgentToolManager
from ..tools.exceptions import AgentExecutionError
from .solve.interface import AgentSolveInterface
from .solve.result import SolveResult
from .validator import InterfaceValidator

logger = logging.getLogger(__name__)


class AgentWrapper:
    """Unified wrapper for agent operations."""

    def __init__(
        self,
        agent_info: dict,
        tool_registry: Any = None,
        agent_id: str | None = None,
        assigned_tools: list[str] | None = None,
        runtime: Any = None,
    ) -> None:
        """
        Initialize the enhanced agent wrapper with Phase 3 features.

        Args:
            agent_info: Agent information from AgentLoader
            tool_registry: Optional tool registry for tool capabilities
            agent_id: Unique identifier for this agent
            assigned_tools: List of external tools assigned to this agent
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

        # Phase 3: Initialize managers
        self.tool_manager = AgentToolManager(self.manifest)
        self.knowledge_manager = KnowledgeManager()

        # Phase 3.2: Initialize solve() components
        self.llm_decision_engine = LLMDecisionMaker()
        self._custom_solve_agent: AgentSolveInterface | None = None

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

    def __getattr__(self, method_name: str) -> Any:
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

        # Check if it's the solve method first
        if method_name == "solve":
            return self.solve

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

        def method_caller(*args: Any, **kwargs: Any) -> Any:
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

                # Resolve relative file paths to absolute paths
                resolved_kwargs = self._resolve_file_paths(kwargs)

                return self.execute(method_name, resolved_kwargs)

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
    ) -> None:
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

    # Simplified tool execution using unified tool manager
    def execute_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a tool with access control (simplified)."""
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

    def get_tool_metadata(self, tool_name: str) -> dict[str, Any] | None:
        """Get metadata for a tool."""
        if not self.tool_registry:
            return None

        # Check if tool is assigned to this agent
        if tool_name not in self.assigned_tools:
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

    def can_access_tool(self, tool_name: str) -> bool:
        """Check if agent can access a specific tool."""
        return tool_name in self.assigned_tools

    def get_assigned_tools(self) -> list[str]:
        """Get list of tools assigned to this agent."""
        return self.assigned_tools.copy()

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

    def _resolve_file_paths(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Resolve relative file paths to absolute paths in parameters.

        This ensures that when the agent runs in a subprocess with a different
        working directory, file paths are still accessible.

        Args:
            parameters: Dictionary of method parameters

        Returns:
            Dictionary with resolved file paths
        """
        resolved_params = parameters.copy()

        # Common file path parameter names to check
        file_path_keys = [
            "file_path",
            "file",
            "path",
            "input_file",
            "output_file",
            "source_file",
            "target_file",
            "document",
            "paper",
            "pdf",
            "image",
            "video",
            "audio",
            "data_file",
            "config_file",
        ]

        for key, value in resolved_params.items():
            # Check if this looks like a file path parameter
            if isinstance(value, str) and (
                key.lower() in file_path_keys
                or any(
                    keyword in key.lower()
                    for keyword in ["file", "path", "document", "paper"]
                )
            ):

                # If it's a relative path, resolve it to absolute
                if not os.path.isabs(value):
                    # Resolve relative to current working directory
                    resolved_path = os.path.abspath(value)
                    resolved_params[key] = resolved_path
                    logger.debug(
                        f"Resolved relative path '{value}' to absolute path "
                        f"'{resolved_path}'"
                    )

        return resolved_params

    def execute(self, method: str, parameters: dict[str, Any]) -> Any:
        """
        Execute an agent method with monitoring support.

        Args:
            method: Name of the method to execute
            parameters: Parameters for the method

        Returns:
            Result from agent execution
        """
        if not self.runtime:
            raise AgentExecutionError("No runtime available for agent execution")

        # Check if we have a MonitoredProcessManager
        if hasattr(self.runtime.process_manager, "execute_agent_with_monitoring"):
            # Use monitoring-enabled execution but preserve original result structure
            monitored_result = (
                self.runtime.process_manager.execute_agent_with_monitoring(
                    agent_path=self.path,
                    method=method,
                    parameters=parameters,
                    tool_context=json.loads(self.get_tool_context_json()),
                )
            )

            # If monitoring failed to parse, fall back to standard execution
            if (
                "error" in monitored_result
                and "Invalid JSON response" in monitored_result["error"]
            ):
                logger.warning(
                    "Monitoring failed to parse agent output, "
                    "falling back to standard execution"
                )
                return self.runtime.execute_agent(
                    namespace=self.namespace,
                    agent_name=self.name,
                    method=method,
                    parameters=parameters,
                    tool_context=json.loads(self.get_tool_context_json()),
                )

            # Return the full monitoring result (includes execution_time)
            return monitored_result
        else:
            # Use standard execution
            return self.runtime.execute_agent(
                namespace=self.namespace,
                agent_name=self.name,
                method=method,
                parameters=parameters,
                tool_context=json.loads(self.get_tool_context_json()),
            )

    # Phase 3: Enhanced tool management methods

    def add_external_tools(self, tool_names: list[str]) -> None:
        """Add external tools from user."""
        if self.tool_registry is None:
            raise ValueError("Tool registry not available")

        # Use the unified tool manager to assign tools
        assigned_tools = self.tool_manager.assign_tools_to_agent(
            self.agent_id, tool_names
        )
        self.assigned_tools.extend(assigned_tools)
        logger.info(f"Added external tools to agent {self.agent_id}: {assigned_tools}")

    def disable_builtin_tools(self, tool_names: list[str]) -> None:
        """Disable specified built-in tools."""
        self.tool_manager.disable_builtin_tools(tool_names)
        logger.info(f"Disabled built-in tools for agent {self.agent_id}: {tool_names}")

    def enable_builtin_tools(self, tool_names: list[str]) -> None:
        """Enable specified built-in tools."""
        self.tool_manager.enable_builtin_tools(tool_names)
        logger.info(f"Enabled built-in tools for agent {self.agent_id}: {tool_names}")

    def get_builtin_tools(self) -> dict[str, Any]:
        """Get built-in tools information."""
        return {
            name: {
                "description": tool.description,
                "required": tool.required,
                "enabled": tool.enabled,
                "parameters": tool.parameters,
            }
            for name, tool in self.tool_manager.builtin_tools.items()
        }

    def get_all_available_tools(self) -> list[str]:
        """Get all available tools (enabled built-in + external)."""
        return self.tool_manager.get_all_available_tools(self.agent_id)

    def is_builtin_tool_available(self, tool_name: str) -> bool:
        """Check if a built-in tool is available."""
        return self.tool_manager.is_builtin_tool_available(tool_name)

    def is_builtin_tool_required(self, tool_name: str) -> bool:
        """Check if a built-in tool is required."""
        return self.tool_manager.is_builtin_tool_required(tool_name)

    def validate_builtin_tool_parameters(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> list[str]:
        """Validate parameters for a built-in tool."""
        return self.tool_manager.validate_builtin_tool_parameters(tool_name, parameters)

    # Phase 3: Knowledge management methods

    def inject_knowledge(
        self, knowledge_text: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """Inject knowledge into agent context."""
        knowledge_id = self.knowledge_manager.inject_knowledge(knowledge_text, metadata)
        logger.info(f"Injected knowledge into agent {self.agent_id}: {knowledge_id}")
        return knowledge_id

    def get_knowledge(self) -> str:
        """Get injected knowledge."""
        return self.knowledge_manager.get_knowledge()

    def get_knowledge_metadata(self) -> dict[str, Any]:
        """Get knowledge metadata."""
        return self.knowledge_manager.get_metadata()

    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available."""
        return self.knowledge_manager.is_knowledge_available()

    def clear_knowledge(self) -> None:
        """Clear injected knowledge."""
        self.knowledge_manager.clear_knowledge()
        logger.info(f"Cleared knowledge for agent {self.agent_id}")

    def search_knowledge(self, query: str) -> str | None:
        """Search knowledge for relevant information."""
        return self.knowledge_manager.search_knowledge(query)

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get summary of current knowledge."""
        return self.knowledge_manager.get_knowledge_summary()

    # Phase 3: Enhanced tool execution with built-in tool support

    def execute_tool_enhanced(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """Execute tool with enhanced Phase 3 support (built-in + external)."""
        # Check if it's a built-in tool
        if tool_name in self.tool_manager.builtin_tools:
            if not self.tool_manager.builtin_tools[tool_name].enabled:
                raise ValueError(f"Built-in tool '{tool_name}' is disabled")

            # Validate parameters
            errors = self.tool_manager.validate_builtin_tool_parameters(
                tool_name, parameters
            )
            if errors:
                raise ValueError(
                    f"Tool parameter validation failed: {'; '.join(errors)}"
                )

            # Execute via runtime
            if self.runtime:
                return self.runtime.execute_tool(tool_name, parameters)
            else:
                raise ValueError("No runtime available for built-in tool execution")

        # Check if it's an external tool
        elif tool_name in self.assigned_tools:
            return self.execute_tool(tool_name, **parameters)

        else:
            available_builtin = self.tool_manager.get_available_builtin_tools()
            available_external = self.assigned_tools
            all_available = available_builtin + available_external
            raise ValueError(
                f"Tool '{tool_name}' not found. Available tools: {all_available}"
            )

    # Phase 3: Enhanced metadata access

    def get_tool_summary(self) -> dict[str, Any]:
        """Get comprehensive tool summary."""
        return self.tool_manager.get_tool_summary(self.agent_id)

    def get_agent_summary(self) -> dict[str, Any]:
        """Get comprehensive agent summary."""
        return {
            "basic_info": {
                "name": self.name,
                "namespace": self.namespace,
                "version": self.version,
                "description": self.description,
                "path": self.path,
            },
            "capabilities": {
                "methods": self.methods,
                "has_runtime": self.runtime is not None,
                "has_tool_registry": self.tool_registry is not None,
            },
            "tools": self.get_tool_summary(),
            "knowledge": self.get_knowledge_summary(),
        }

    # Phase 3.2: Intelligent solve() method

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> SolveResult:
        """
        Intelligently solve a user query by selecting and executing the most
        appropriate method.

        This method implements the Phase 3.2 intelligent solve functionality:
        1. Check if agent has custom solve() method
        2. If yes, delegate to custom solve()
        3. If no, use LLM to select best method and extract parameters
        4. Execute selected method with extracted parameters

        Args:
            query: User's natural language query
            context: Optional context information (tools, knowledge, etc.)
            **kwargs: Additional parameters

        Returns:
            SolveResult with execution details and results
        """
        start_time = time.time()

        try:
            # Check if agent has custom solve() method
            if self._has_custom_solve():
                return self._execute_custom_solve(query, context, **kwargs)
            else:
                return self._execute_framework_solve(query, context, **kwargs)

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in solve() method: {e}")
            # Return error as SolveResult
            return SolveResult(
                result=None,
                success=False,
                error=str(e),
                execution_time=execution_time,
                method_used="solve",
                method_type="framework",
            )

    def _has_custom_solve(self) -> bool:
        """Check if agent has a custom solve() method."""
        try:
            if self._custom_solve_agent is None:
                # Try to load the agent and check for solve method
                agent = self._load_custom_solve_agent()
                self._custom_solve_agent = agent

            return self._custom_solve_agent is not None
        except Exception as e:
            logger.debug(f"Could not check for custom solve method: {e}")
            return False

    def _load_custom_solve_agent(self) -> AgentSolveInterface | None:
        """Load agent instance and check for custom solve method."""
        try:
            if not self.runtime:
                return None

            # Try to import and instantiate the agent
            # This is a simplified approach - in practice, you'd need more robust
            # loading
            agent_module = self._load_agent_module()
            if agent_module and hasattr(agent_module, "solve"):
                # Check if it implements the interface
                if isinstance(agent_module, AgentSolveInterface):
                    return agent_module
                elif callable(getattr(agent_module, "solve", None)):
                    # Create a wrapper for non-interface agents
                    return CustomSolveWrapper(agent_module)

            return None
        except Exception as e:
            logger.debug(f"Could not load custom solve agent: {e}")
            return None

    def _load_agent_module(self) -> Any:
        """Load the agent module (simplified implementation)."""
        # This is a placeholder - in practice, you'd need to implement
        # proper module loading based on the agent path
        return None

    def _execute_custom_solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> SolveResult:
        """Execute custom solve method if available."""
        start_time = time.time()

        try:
            # Prepare context with tools and knowledge
            full_context = self._prepare_solve_context(context)

            # Execute custom solve method
            if not self._custom_solve_agent:
                raise RuntimeError("No custom solve agent available")

            # This code is reachable because the raise above is conditional
            result = self._custom_solve_agent.solve(query, full_context, **kwargs)
            execution_time = time.time() - start_time

            # Convert result to SolveResult if it's not already
            if isinstance(result, SolveResult):
                return result
            else:
                return SolveResult(
                    result=result,
                    success=True,
                    method_used="custom_solve",
                    method_type="custom",
                    execution_time=execution_time,
                )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in custom solve method: {e}")
            return SolveResult(
                result=None,
                success=False,
                error=str(e),
                execution_time=execution_time,
                method_used="custom_solve",
                method_type="custom",
            )

    def _execute_framework_solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> SolveResult:
        """Execute framework-level solve using LLM method selection."""
        start_time = time.time()

        try:
            # Prepare context
            full_context = self._prepare_solve_context(context)

            # Get available methods with metadata
            agent_methods = self._get_method_metadata()

            if not agent_methods:
                return SolveResult(
                    result=None,
                    success=False,
                    error="No methods available for this agent",
                    execution_time=time.time() - start_time,
                    method_used="framework_solve",
                    method_type="framework",
                )

            # Use LLM to select method
            method_name, confidence, reasoning = self.llm_decision_engine.select_method(  # type: ignore[attr-defined]
                query, agent_methods, full_context
            )

            if not method_name:
                return SolveResult(
                    result=None,
                    success=False,
                    error="Could not select appropriate method",
                    execution_time=time.time() - start_time,
                    method_used="framework_solve",
                    method_type="framework",
                )

            # Get method parameters
            method_info = self.get_method_info(method_name)
            method_parameters = method_info.get("parameters", {})

            # Extract parameters from query
            extracted_params, param_confidence, param_reasoning = (
                self.llm_decision_engine.extract_parameters(  # type: ignore[attr-defined]
                    query, method_name, method_parameters, full_context
                )
            )

            # Execute the selected method
            result = self.execute(method_name, extracted_params)

            execution_time = time.time() - start_time

            # Combine reasoning (for future use if needed)
            # combined_reasoning = f"Method selection: {reasoning}. "
            # f"Parameter extraction: {param_reasoning}"
            # combined_confidence = min(confidence, param_confidence)

            # Convert result to SolveResult
            if isinstance(result, SolveResult):
                return result
            else:
                return SolveResult(
                    result=result,
                    success=True,
                    method_used=method_name,
                    method_type="framework",
                    execution_time=execution_time,
                    confidence=confidence,
                    reasoning=reasoning,
                )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in framework solve method: {e}")
            return SolveResult(
                result=None,
                success=False,
                error=str(e),
                execution_time=execution_time,
                method_used="framework_solve",
                method_type="framework",
            )

    def _prepare_solve_context(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Prepare context for solve method with tools and knowledge."""
        full_context = context or {}

        # Add tool context
        if self.assigned_tools:
            full_context["available_tools"] = self.assigned_tools
            full_context["tool_descriptions"] = {
                tool: self.get_tool_metadata(tool) for tool in self.assigned_tools
            }

        # Add knowledge context
        if self.is_knowledge_available():
            full_context["knowledge"] = self.get_knowledge()
            full_context["knowledge_metadata"] = self.get_knowledge_metadata()

        # Add agent information
        full_context["agent_info"] = {
            "name": self.name,
            "namespace": self.namespace,
            "version": self.version,
            "description": self.description,
            "methods": self.methods,
        }

        return full_context

    def _get_method_metadata(self) -> list[dict[str, Any]]:
        """Get metadata for all available methods."""
        methods = []

        for method_name in self.methods:
            try:
                method_info = self.get_method_info(method_name)
                methods.append(
                    {
                        "name": method_name,
                        "description": method_info.get(
                            "description", f"Execute {method_name}"
                        ),
                        "parameters": method_info.get("parameters", {}),
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get metadata for method {method_name}: {e}")
                methods.append(
                    {
                        "name": method_name,
                        "description": f"Execute {method_name}",
                        "parameters": {},
                    }
                )

        return methods


class CustomSolveWrapper(AgentSolveInterface):
    """Wrapper for agents with custom solve methods."""

    def __init__(self, agent_instance: Any) -> None:
        self.agent_instance = agent_instance

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Delegate to the agent's custom solve method."""
        return self.agent_instance.solve(query, context, **kwargs)

    def get_solve_capabilities(self) -> dict[str, Any]:
        """Get solve capabilities from the wrapped agent."""
        if hasattr(self.agent_instance, "get_solve_capabilities"):
            result = self.agent_instance.get_solve_capabilities()
            return (
                result
                if isinstance(result, dict)
                else {
                    "has_custom_solve": True,
                    "description": "Custom solve method (wrapped)",
                    "version": "1.0.0",
                }
            )
        return {
            "has_custom_solve": True,
            "description": "Custom solve method (wrapped)",
            "version": "1.0.0",
        }
