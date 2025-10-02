"""Simplified agent wrapper - orchestration layer only."""

import logging
from typing import Any

from ..interfaces import (
    KnowledgeManagerProtocol,
    ToolManagerProtocol,
)
from .agent_info import AgentInfo
from .method_executor import MethodExecutor
from .solve import SolveEngine
from .validator import InterfaceValidator

logger = logging.getLogger(__name__)


class AgentWrapper:
    """Simplified agent wrapper - orchestration layer only."""

    def __init__(
        self,
        agent_info: dict,
        tool_registry: Any = None,
        agent_id: str | None = None,
        assigned_tools: list[str] | None = None,
        runtime: Any = None,
        knowledge_manager: KnowledgeManagerProtocol | None = None,
        tool_manager: ToolManagerProtocol | None = None,
    ) -> None:
        """
        Initialize the simplified agent wrapper.

        Args:
            agent_info: Agent information from AgentLoader
            tool_registry: Optional tool registry for tool capabilities
            agent_id: Unique identifier for this agent
            assigned_tools: List of external tools assigned to this agent
            runtime: Optional runtime for executing methods
            knowledge_manager: Optional knowledge manager (injected)
            tool_manager: Optional tool manager (injected)
        """
        # Core components
        self.agent_info = AgentInfo(agent_info)
        self.method_executor = MethodExecutor(self)

        # Get LLM service for solve engine
        llm_service = None
        try:
            from ..llm import get_shared_llm_service

            llm_service = get_shared_llm_service()
        except ImportError:
            pass  # LLM service not available

        self.solve_engine = SolveEngine(self, llm_service)  # type: ignore[arg-type]

        # Use dependency injection or create defaults
        if knowledge_manager is not None:
            self.knowledge_manager = knowledge_manager
        else:
            # Import here to avoid circular dependency
            from ..knowledge import KnowledgeManager

            self.knowledge_manager = KnowledgeManager()  # type: ignore[assignment]

        if tool_manager is not None:
            self.tool_manager = tool_manager
        else:
            # Import here to avoid circular dependency
            from ..mcp.agent_tool_manager import AgentToolManager

            self.tool_manager = AgentToolManager(agent_info.get("manifest", {}))

        # Backward compatibility properties
        self.agent_id = agent_id or self.agent_info.agent_id
        self.name = self.agent_info.name
        self.namespace = self.agent_info.namespace
        self.agent_name = self.agent_info.agent_name
        self.path = self.agent_info.path
        self.version = self.agent_info.version
        self.description = self.agent_info.description
        self.methods = self.agent_info.methods
        self.dependencies = self.agent_info.dependencies
        self.manifest = self.agent_info.manifest
        self.interface = self.agent_info.interface

        # Additional properties
        self.tool_registry = tool_registry
        self.assigned_tools = assigned_tools or []
        self.runtime = runtime
        self.interface_validator = InterfaceValidator()

    # Core delegation methods
    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Delegate to solve engine."""
        return self.solve_engine.solve(query, context, **kwargs)

    def execute(self, method: str, parameters: dict[str, Any] | None = None) -> Any:
        """Delegate to method executor."""
        return self.method_executor.execute(method, parameters or {})

    def has_method(self, method_name: str) -> bool:
        """Check if agent has method."""
        return self.agent_info.has_method(method_name)

    def get_method_info(self, method_name: str) -> dict[str, Any]:
        """Get method information."""
        return self.agent_info.get_method_info(method_name)

    # Tool management (delegate to existing tool_manager)
    def assign_tools(self, tool_names: list[str]) -> None:
        """Assign tools to agent."""
        if self.tool_registry:
            self.tool_registry.assign_tools_to_agent(self.agent_id, tool_names)
            # Also update the tool manager
            self.tool_manager.assign_tools_to_agent(self.agent_id, tool_names)
            self.assigned_tools = tool_names.copy()
        else:
            raise RuntimeError("No tool registry available for tool assignment")

    def get_tool_context_json(self) -> str:
        """Get tool context as JSON."""
        import json

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

        # Get tool information from registry
        tool_descriptions = {}
        tool_usage_examples = {}
        tool_parameters = {}
        tool_return_types = {}
        tool_namespaces = {}

        for tool_name in self.assigned_tools:
            try:
                tool_metadata = self.tool_registry.get_tool_metadata(tool_name)
                if tool_metadata:
                    tool_descriptions[tool_name] = tool_metadata.description
                    tool_usage_examples[tool_name] = (
                        tool_metadata.examples[0] if tool_metadata.examples else ""
                    ) or ""
                    # Convert parameters to JSON-serializable format
                    params = tool_metadata.parameters or {}
                    tool_parameters[tool_name] = {
                        k: str(v) if isinstance(v, type) else v
                        for k, v in params.items()
                    }
                    tool_return_types[tool_name] = (
                        str(tool_metadata.return_type)
                        if tool_metadata.return_type
                        else "string"
                    )
                    tool_namespaces[tool_name] = tool_metadata.namespace or "custom"
            except Exception as e:
                logger.warning(f"Could not get metadata for tool {tool_name}: {e}")
                tool_descriptions[tool_name] = f"Tool: {tool_name}"

        # Ensure all values are JSON serializable
        def make_serializable(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, type):
                return str(obj)
            else:
                return obj

        return json.dumps(
            make_serializable(
                {
                    "available_tools": self.assigned_tools,
                    "tool_descriptions": tool_descriptions,
                    "tool_usage_examples": tool_usage_examples,
                    "tool_parameters": tool_parameters,
                    "tool_return_types": tool_return_types,
                    "tool_namespaces": tool_namespaces,
                }
            )
        )

    def get_tool_metadata(self, tool_name: str) -> dict[str, Any] | None:
        """Get tool metadata."""
        if self.tool_registry:
            metadata = self.tool_registry.get_tool_metadata(tool_name)
            return metadata if isinstance(metadata, dict) else None
        return None

    def can_access_tool(self, tool_name: str) -> bool:
        """Check if agent can access tool."""
        return self.tool_manager.has_tool_access(self.agent_id, tool_name)

    def get_assigned_tools(self) -> list[str]:
        """Get assigned tools."""
        return self.assigned_tools.copy()

    def add_external_tools(self, tool_names: list[str]) -> None:
        """Add external tools to agent."""
        if self.tool_registry:
            self.tool_registry.assign_tools_to_agent(self.agent_id, tool_names)
            # Also update the tool manager
            self.tool_manager.assign_tools_to_agent(self.agent_id, tool_names)
            self.assigned_tools.extend(tool_names)
        else:
            raise RuntimeError("No tool registry available for tool assignment")

    def disable_builtin_tools(self, tool_names: list[str]) -> None:
        """Disable built-in tools."""
        self.tool_manager.disable_builtin_tools(tool_names)

    def enable_builtin_tools(self, tool_names: list[str]) -> None:
        """Enable built-in tools."""
        self.tool_manager.enable_builtin_tools(tool_names)

    def get_builtin_tools(self) -> dict[str, Any]:
        """Get built-in tools."""
        return {
            name: {
                "description": tool.description,
                "parameters": tool.parameters,
                "enabled": tool.enabled,
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

    def execute_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a tool."""
        # Map args and kwargs to parameters
        parameters = {}
        if args:
            parameters["args"] = args
        if kwargs:
            parameters.update(kwargs)

        # Use tool registry to execute tool
        if self.tool_registry:
            return self.tool_registry.execute_tool(tool_name, parameters)
        else:
            raise RuntimeError("No tool registry available for tool execution")

    def execute_tool_enhanced(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """Execute a tool with enhanced parameters."""
        if self.tool_registry:
            return self.tool_registry.execute_tool(tool_name, parameters)
        else:
            raise RuntimeError("No tool registry available for tool execution")

    def get_tool_summary(self) -> dict[str, Any]:
        """Get tool summary."""
        return self.tool_manager.get_tool_summary(self.agent_id)

    # Knowledge management (delegate to existing knowledge_manager)
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
        """Get knowledge summary."""
        return self.knowledge_manager.get_knowledge_summary()

    # Summary methods
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return self.agent_info.to_dict()

    def __repr__(self) -> str:
        """String representation."""
        return self.agent_info.__repr__()

    # Magic method for dynamic method calls
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
            raise AttributeError(
                f"Method '{method_name}' not found in agent '{self.name}'! "
                f"Available methods: {available_methods}"
            )

        def method_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper function for dynamic method calls."""
            # Map args and kwargs to parameters using MethodExecutor logic
            parameters = {}
            if args:
                parameters["args"] = args
            if kwargs:
                parameters.update(kwargs)

            # Use MethodExecutor to handle parameter mapping and execution
            return self.method_executor.execute(method_name, parameters)

        return method_wrapper
